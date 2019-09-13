.. River Network Analysis documentation master file, created by
   sphinx-quickstart on Mon Sep  2 16:11:36 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

River Network Analysis
======================

Welcome to the documentation of the code belonging to my master thesis.
In this thesis I have used Muskingum routing principles and applied them to a network structure.
Documenting is a ongoing process and will emphasize on the developed scripts.


Literature and principles
-------------------------
There is plenty of literature available on Muskingum routing.
Here is a short list:

* For a comprehensive overview of flood routing and other hydrology concepts the
  `National Engineering Handbook Hydrology <https://www.nrcs.usda.gov/wps/portal/nrcs/detailfull/national/water/manage/hydrology/?cid=stelprdb1043063>`_ gives a good overview.
  `Chapter 17 <https://directives.sc.egov.usda.gov/OpenNonWebContent.aspx?content=35555.wba>`_, section channel flood routing methods explains the Muskingum methods.
* `For the full derivation of the muskingum equation see Todini 2007 <https://www.hydrol-earth-syst-sci.net/11/1645/2007/hess-11-1645-2007.pdf>`_
* `This is a very clear and practical example by University of Colorado Boulder <http://www.engr.colostate.edu/~ramirez/ce_old/classes/cive322-Ramirez/CE322_Web/Example_MuskingumRouting.htm>`_

This documentation is divided into two sections.
In the first section the basic parts or building blocks of the model are presented and analysed.
In the second section small networks are tested and analysed. 
This section also explains some concepts on how to calculate flows in these networks.



.. toctree::
   :maxdepth: 2
   :caption: Basic Parts:
   
   single-reach.ipynb
   single-confluence.ipynb
   single-bifurcation.ipynb
   
.. toctree::
   :maxdepth: 2
   :caption: Networks:
   
   network-structure-1.ipynb
   network-structure-2.ipynb


.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
