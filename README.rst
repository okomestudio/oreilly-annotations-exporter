****************************
oreilly-annotations-exporter
****************************

*oreilly-annotations-exporter* for Python.

The motivation for this tool is to transform and structure the exported
annotations from O’Reilly Learning in ways that are easier to import into
one’s own note-taking setup.

The O’Reilly Learning does have manual annotation export tool which generates
CSV dumps. They contain insufficient metadata to understand the location of
annotations in the original document. The API provides more info to do this.


Installation
============

.. code-block:: sh

   $ pip install git+https://github.com/okomestudio/oreilly-annotations-exporter


Help
====

.. code-block:: sh

   $ oreilly-annotations-exporter --help


Using *oreilly-annotations-exporter*
====================================

If this is the first time running the command and the JSON API response dump has
not been saved, follow `Obtaining Cookies`_ first.

With the cookies saved to the working directory, run

.. code-block:: sh

   $ oreilly-annotations-exporter my-dump.json

will hit the API, download, and save the JSON responses to the file named
*my-dump.json*. Subsequent invocations will use the JSON dump without hitting
the API.


Exporting in Desired Format
---------------------------

The command generates and sends output to the standard output stream, which you
should redirect to a file for persistence.

.. code-block:: sh

   $ oreilly-annotations-exporter my-dump.json > my-output.csv

This will generate a CSV export similar to the one O’Reilly generates in their
UI. The output format is controlled by the *--export* option, with which the
exporter can be specified.

The tool comes with a couple of built-in exporters, *csv* (default, similar to
the default O’Reilly export) and *raw_xml*. The latter produces raw XML with
reconstructed document structure.

To support wider export format, a custom exporter can be used as a plugin. See
`Writing Exporter Plugin`_ for detail.



Obtaining Cookies
-----------------

1. Make sure that you are logged in to O’Reilly with your browser.

2. Open the Developer Tools (e.g., right-click “inspect” in Chrome). Open the
   Network tab.

3. Visit the following URL:

   - `https://learning.oreilly.com/api/v1/annotations/all/`_

4. Locate the “request headers” in the network tab. You should find the
   “Cookie:” item with the corresponding text.

5. Save that text to a file named *cookies* in the working directory. This will
   be picked up by *oreilly-annotations-exporter*.


.. _https://learning.oreilly.com/api/v1/annotations/all/: https://learning.oreilly.com/api/v1/annotations/all/


Writing Exporter Plugin
=======================

Custom exporters can be written as plugins. The tool will pick up Python module
files in the working directory (or the *plugins* directory in it). For example,
if you have a Python module file named *myexporter.py*,

.. code-block:: sh

   $ oreilly-annotations-exporter my-dump.json --export myexporter

will use the exporter defined in *myexporter.py*.

A custom exporter only needs to define a function named *export* with just one
argument. The function will be passed a *dict* variable which maps epub ID
(ISBN13) to the ElementTree object representing the document structure with
annotations embedded, for which *raw_xml* export can be used for inspection.

See *plugins/org.py* for example.
