import timeit
import sys,time
import random
import sqlite3
import copy
import numpy
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from ConfigParser import SafeConfigParser # For use with Python 2.7
from neuroml import NeuroMLDocument
from neuroml import Network
from neuroml import ExpOneSynapse
from neuroml import Population
from neuroml import Annotation
from neuroml import Property
from neuroml import Cell
from neuroml import Location
from neuroml import Instance
from neuroml import Morphology
from neuroml import Point3DWithDiam
from neuroml import Segment
from neuroml import SegmentParent
from neuroml import Projection
from neuroml import Connection

import neuroml.writers as writers

soma_diam = 10
soma_len = 10

def generate_with_morphology(db_name,cfg_file) :

    parser = SafeConfigParser()
    parser.read(cfg_file)
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("select distinct name from swc_data order by name")
    rets = cursor.fetchall()
    names =[]
    c=0
    for entity in rets :

       names.append(entity[0])

    prefix=""
    if db_name.startswith(".."):
        prefix = db_name.split("/")
        print ".. prefix: ", prefix,"\nNot sure this works correctly..."
    else:
        prefix = "/".join(db_name.split(".")[0].split("/")[:-1])
        print "prefix: ", prefix

    morphology = Morphology()

    p = Point3DWithDiam(x=0,y=0,z=0,diameter=soma_diam)
    d = Point3DWithDiam(x=soma_len,y=0,z=0,diameter=soma_diam)
    soma = Segment(proximal=p, distal=d, name = 'Soma', id = 0)

    morphology.segments.append(soma)
    parent_seg = soma

    morphology.id = "NeuroMLMorphology"
    return morphology
   
    all_points = {}
    soma_radius = None

    for name in names :
        all_points[name] = {}
        cursor.execute("select * from swc_data where name=? order by id",(str(name),) )
        rets = cursor.fetchall()
        points = {}
        is_soma = True
        
        print 'processing: ', name
        for entity in rets :
            contents = {}
            index = entity[0]
            if is_soma:
                points['soma'] = (entity[3],entity[4],entity[5])
                soma_radius = parser.getint(entity[1].split("__")[0],"soma_radius")
                print "found soma_radius: ", soma_radius
                is_soma = False
            contents['name'] = entity[1]
            contents['swc_type'] = entity[2]
            contents['f'] = (entity[3],entity[4],entity[5])
            contents['t'] = (entity[6],entity[7],entity[8])
            contents['r'] = entity[9]
            points[entity[0]] =contents        
        all_points[name] = points
def _from_point(p,points) :
    for index in points:
        if index == 'soma' :
            continue
        if points[index]['t'] == p :
            return index
    print "not found: ", p,' [should not happen]'


if __name__=="__main__" :
    cfg_file = sys.argv[1]
    db_name = sys.argv[2]
    generate_with_morphology(db_name,cfg_file)

def run():

    cell_num = 2
    
    nml_doc = NeuroMLDocument(id="demo_attraction")

    net = Network(id="demo_attraction")
    nml_doc.networks.append(net)

    for cell_id in range(0,cell_num):

        cell = Cell(id="Cell_%i"%cell_id)

        cell.morphology = generate_with_morphology(db_name,cfg_file)
        
        nml_doc.cells.append(cell)

        pop = Population(id="Pop_%i"%cell_id, component=cell.id, type="populationList")
        net.populations.append(pop)
       
        inst = Instance(id="0")
        pop.instances.append(inst)

        inst.location = Location(x=0, y=0, z=0)
    
        
    
    #######   Write to file  ######    
 
     	nml_file = 'demo_attraction/demo_attraction.net.nml'
     	writers.NeuroMLWriter.write(nml_doc, nml_file)
    
    	print("Written network file to: "+nml_file)


    ###### Validate the NeuroML ######    

    from neuroml.utils import validate_neuroml2

    validate_neuroml2(nml_file)
run()
