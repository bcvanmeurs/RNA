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

This documentation is divided into three sections.
In the first section the basic parts or building blocks of the model are presented and analysed.
In the second section small networks are tested and analysed. 
This section also explains some concepts on how to calculate flows in these networks.
The third section shows some code to extract the Ganges Brahmaputra watershed from the Hydrosheds dataset.
(Code not well documented yet)



.. toctree::
   :maxdepth: 2
   :caption: Basic Parts:

   A-single-reach.ipynb
   A-single-confluence.ipynb
   A-single-bifurcation.ipynb
   A-model-verification.ipynb

.. toctree::
   :maxdepth: 2
   :caption: Networks:

   B-network-structure-1.ipynb
   B-network-structure-2.ipynb

.. toctree::
   :maxdepth: 2
   :caption: Ganges Brahmaputra GIS:

   C-gis/01-create-hydroshed.ipynb

.. toctree::
   :maxdepth: 2
   :caption: Simulation:

   D-simulation/01-modelling.ipynb
   D-simulation/02-plotting-results.ipynb

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
