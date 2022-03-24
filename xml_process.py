import sys
import xml.etree.ElementTree as ET
import os
from os import path
import re
import copy

class Xml:
    def __init__(self):
        self.path_MallaDir = path.join(os.getcwd(), "Mallas")   # La ruta a la carpeta Mallas
        self.path_malla = ""    # La ruta completa al xml
        self.malla_name = ""    # ("<nombre de la malla>", ".xml")
        self.xml = None     # La malla parseada a xml

    def start(self):
        files = [path.splitext(path.join(self.path_MallaDir, f)) for f in os.listdir(self.path_MallaDir) if path.isfile(path.join(self.path_MallaDir, f))]
        xmls = [x for x in files if x[1].lower() == ".xml"]
        mallas = [m for m in xmls if re.search("^CR-MX.+-T02$", path.basename(m[0]))]

        print("Las mallas que se encuentran dentro de la carpeta Mallas son:")
        for m in mallas:
            print(path.basename((m[0]))+m[1])
        malla_input = input("Introduzca la malla con la que deseas trabajar:\n").strip()
        for m in mallas:
            if malla_input == path.basename(m[0])+m[1]:
                try:
                    return self.read_xml(m[0]+m[1])
                except ET.ParseError as e:
                    print("ERROR en la estructura del xml\n"+\
                        "Dentro del elemento que cierra en la linea {}\n".format(e.position[0])+\
                            "hay un elemento no coinciden sus etiquetas de apertura y cierre")
                    sys.exit()
        print("INTRODUZCA UN NOMBRE VALIDO\n")
        return self.start()

    def read_xml(self, malla_path):
        if path.exists(malla_path):
            self.path_malla = malla_path
            self.malla_name = path.splitext(path.basename(malla_path))
            self.xml = ET.parse(malla_path) # ElementTree object
            deftable_elem = self.xml.getroot() # <DEFTABLE>
            folder_elems = deftable_elem.findall("FOLDER")
            folder_elem = folder_elems[0] # <FOLDER>
            job_elems = folder_elem.findall("JOB") # Lista que contiene los <JOB>
            return {
                "xml": self.xml, # ElementTree
                "deftable_elem": deftable_elem, # <DEFTABLE> Element
                "folder_elem": folder_elem, # <FOLDER> Element
                "job_elems": job_elems # <Lista que contiene los <JOB> Element>
            }
        else:
            print("VERIFIQUE QUE EL XML EXISTA\n")
            return self.start()
#-----------------------------------------------------------
    def checkSentry(self, nodes):
        jobs_e = nodes["job_elems"]
        for i_job in range(len(jobs_e)):
            job_e = jobs_e[i_job]
            '''AQUI PONER UN IF CUANDO SEPA
            QUE JOBS SE DEBEN EXCLUIR DE SENTRY. PREGUNTAR'''
            #--------------------------- Exclusion de jobs
            job_attr = job_e.attrib # Diccionario con los atributos del job
            try:
                job_attr["MEMNAME"]
                continue # Es un job de extraccion
            except KeyError: # No es un job de extracción
                pass
            if job_attr["JOBNAME"] in self.read_txt("jobs_to_exclude.txt"): # Excluye los jobs dentro del txt
                continue
            else: pass
            #--------------------------- Primera validacion. <JOB>
            if job_attr["RUN_AS"] != "sentry" \
            or job_attr["TASKTYPE"] != "Command" \
            or job_attr["NODEID"] != "MX-SENTRY-00" \
            or job_attr["CMDLINE"] != "/opt/datio/sentry-mx/dataproc_sentry.py %%SENTRY_JOB %%SENTRY_OPT '%%SENTRY_PARM'":
                print("EL JOB {} ".format(job_attr["JOBNAME"])+\
                    "NO INTEGRA SENTRY")
                sys.exit()
            #--------------------------- Segunda validacion. <VARIABLE>
            job_vars = job_e.findall("VARIABLE")
            flag0 = False
            flag1 = False
            flag2 = False
            for i_var in range(len(job_vars)):
                var_e = job_vars[i_var]
                var_attr = var_e.attrib
                if var_attr["NAME"] == "%%SENTRY_JOB" and\
                re.match(
                    '''^-ns\s+mx\..+\.app-id-[0-9]+\.pro\s+-jn\s+.+\s+-o\s+%%ORDERID''',
                    var_attr["VALUE"]
                ):
                    flag0 = True
                if var_attr["NAME"] == "%%SENTRY_OPT":
                    flag1 = True
                if var_attr["NAME"] == "%%SENTRY_PARM":
                    flag2 = True
            if flag0 and flag1 and flag2: pass
            else:
                print("EL JOB {} ".format(job_attr["JOBNAME"])+\
                    "NO INTEGRA SENTRY")
                sys.exit()
            #--------------------------- Tercera validacion. <QUANTITATIVE>
            job_quant = job_e.findall("QUANTITATIVE")
            for i_quant in range(len(job_quant)):
                quant_e = job_quant[i_quant]
                quant_attr = quant_e.attrib
                if quant_attr["NAME"] != "DATIO_SENTRY_MX":
                    print("EL JOB {} ".format(job_attr["JOBNAME"])+\
                        "NO INTEGRA SENTRY")
                    sys.exit()
        print("La malla integra SENTRY correctamente")
#-----------------------------------------------------------
    def extract_jobs(self):
        new_file_path = path.join(self.path_MallaDir, "{}__EXTRACTED{}".format(self.malla_name[0], self.malla_name[1]))
        xml = copy.deepcopy(self.xml)
        folder = xml.getroot().findall("FOLDER")[0]
        old_folder = copy.deepcopy(folder)
        for job in folder.findall("JOB"):
            folder.remove(job)
        for job_str in self.read_txt("jobs_to_extract.txt"):
            for job in old_folder.findall("JOB"):
                if job_str == job.get("JOBNAME"):
                    folder.append(job)
        xml.write(new_file_path, encoding="utf-8", xml_declaration=True)
#-----------------------------------------------------------
    def accommodate(self, xml):
        xml1 = copy.deepcopy(xml)
        ET.indent(xml1, space="\t", level=0)
        xml1.write(self.path_malla, encoding="utf-8", xml_declaration=True)
#-----------------------------------------------------------
    def read_txt(self, txt):
        path_txt = path.join(self.path_MallaDir, txt)
        if path.exists(path_txt):
            with open(path.join(self.path_MallaDir, txt)) as f:
                return [line.strip() for line in f.readlines()]
        else:
            print('El archivo {} no existe dentro de la carpeta Mallas'.format(txt))
            sys.exit()
            

