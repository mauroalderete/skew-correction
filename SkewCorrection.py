import sys, getopt
import re
import os

class SkewCorrection():
    def __init__(self):
        super().__init__()

    def getValue(self, command, line):
        r = re.search(command + r'-?\d+(\.\d+)?', line)
        if( r == None ):
            return None
        else:
            return float(r.group()[len(command):])
    
    def setValue(self, command, value, line):
        return re.sub(command + r'\d+(\.\d+)?', command + str(value), line)

    def toCorrect(self, data: list, xyerr, xylen):

        xytan = xyerr/xylen

        index = 0
        for line in data:
            if self.getValue('G', line) == 1 or self.getValue('G', line) == 0:
                xin = self.getValue('X', line)
                yin = self.getValue('Y', line)

                if not xin == None and not yin == None:
                    xout = round(xin-yin*xytan, 3)
                    line = self.setValue('X', xout, line)
            
                    data[index] = line
            index += 1

        return data

def main(argv):
    inputfile = ''
    replace = False
    undo = False

    try:
        opts, _ = getopt.getopt(argv, "hvuri:",["undo", "replace", "input="])
    except getopt.GetoptError:
        print('SkewCorrection.py -i <input>')
        sys.exit(0)

    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print('SkewCorrection.py -i <inputfile> -o <outputfile>')
            sys.exit(0)
        elif opt in ("-v", "--version"):
            print('version 0.0.1')
            sys.exit(0)
        elif opt in ("-u", "--undo"):
            print('try undo...')
            undo = True
        elif opt in ("-r", "--replace"):
            replace = True
        elif opt in ("-i", "--input"):
            inputfile = arg
    
    print("SkewCorrection: " + inputfile)
    skew = SkewCorrection()

    if undo:
        if os.path.exists(inputfile[:-len(".gcode")] + ".backup.gcode"):
            print("Restoring...")
            backup = open(inputfile[:-len(".gcode")] + ".backup.gcode", "r")
            source = open(inputfile, "w")
            for b in backup:
                source.write(b)
            print("Restoring complete")
            source.close()
            backup.close()
        else:
            print("ERROR: backup not found")
        sys.exit(0)

    print("Preparing...")
    # limpio los archivos de otras ejecuciones anteriores
    if os.path.exists(inputfile[:-len(".gcode")] + ".backup.gcode"):
        os.remove(inputfile[:-len(".gcode")] + ".backup.gcode")
    if os.path.exists(inputfile[:-len(".gcode")] + ".corrected.gcode"):
        os.remove(inputfile[:-len(".gcode")] + ".corrected.gcode")

    print("Reading...")
    gcode = open(inputfile, "r")
    gcodelines = []
    for g in gcode:
        gcodelines.append(g)
    gcode.close()

    if replace:
        print("Replace = True")
        print("Creating Backup...")
        # realizo un backup de gcode original
        backup = open(inputfile[:-len(".gcode")] + ".backup.gcode", "w")
        for g in gcodelines:
            backup.write(g)
        backup.close()
    
    # obtengo los nuevos valores corregidos
    print("correcting...")
    data = skew.toCorrect(data=gcodelines, xyerr=-3.9, xylen=250)
    
    # sobreescribo el gcode original con los nuevos valores
    if replace:
        # selecciono el mismo archivo fuente para sobreescribirlo
        modified = open(inputfile, "w")
    else:
        print("Reaplace = False")
        # creo un nuevo archivo para no pisar el original
        modified = open(inputfile[:-len(".gcode")] + ".corrected.gcode", "w")

    print("Saving result...")
    for d in data:
        modified.write(d)
    modified.close()

    print("End")

if __name__ == "__main__":
   main(sys.argv[1:])