from netCDF4 import Dataset, num2date, date2num
import sys

def copy_static(i,o):
    #copy dimensions
    for (dn, dim) in i.dimensions.items():
        o.createDimension(dn, len(dim) if not dim.isunlimited() else None)
                            
    #copy variables
    for (vn, ivar) in i.variables.items():
        ovar = o.createVariable(vn, ivar.datatype, ivar.dimensions)
                                                
        #copy variable attributes
        ovar.setncatts({an: ivar.getncattr(an) for an in ivar.ncattrs()})
        ovar[:] = ivar[:]

def concat(i, o):
    for (name, ovar) in o.variables.items():
        if name == "time": #unit->hours
            #calculate time of input files
            for index, fin in enumerate(i):                          
                if index != 0:              
                    ivar = fin.variables[name]
                    ovar[index] = date2num(num2date(ivar[:], ivar.units, ivar.calendar)[0], ovar.units, ovar.calendar)

        elif name in ("Canint", "SWE"):
            for index, fin in enumerate(i):
                if index != 0:
                    ovar[index] = fin.variables[name][:]

            
if __name__ == "__main__":
    fin = sys.argv[1:-1]
    fout = sys.argv[-1]
                       
    input_list = [ Dataset(i) for i in fin ]
    output_file = Dataset(fout, 'w', format="NETCDF4")
                                                                                                   
    copy_static(input_list[0], output_file)     
    concat(input_list, output_file)
