##########################################################################
# NSAp - Copyright (C) CEA, 2015 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

# System import
from __future__ import print_function
from __future__ import division
from collections import OrderedDict
import os
import math
import json

# Reportlab import
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import Spacer
from reportlab.platypus import BaseDocTemplate
from reportlab.platypus import Frame
from reportlab.platypus import Paragraph
from reportlab.platypus import NextPageTemplate
from reportlab.platypus import PageBreak
from reportlab.platypus import PageTemplate
from reportlab.platypus import Flowable
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER


# Get global image resource
LOGO = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                    "resources", "neurospin.png")


def header_and_footer(canvas, doc):
    """ Define the page header and footer.
    """
    if doc.pageTemplate.pagesize is not None:
        width, height = (doc.height, doc.width - 60)
    else:
        width, height = (doc.width, doc.height)
    canvas.saveState()
    canvas.drawImage(
        LOGO, doc.leftMargin, height, width=40 * mm, preserveAspectRatio=True)
    canvas.setFont("Times-Roman", 9)
    canvas.drawString(
        doc.leftMargin, 15 * mm, "Page {0}: {1} - {2}".format(
            doc.page, doc.title.upper(), doc.author.upper()))
    canvas.restoreState()


class PDFcreator(object):
    """ Generate a text/image PDF.
    """
    def __init__(self, author, client, poweredby, project, timepoint,
                 subject, date, title, filename, pagesize=None, left_margin=20,
                 right_margin=20, top_margin=20, bottom_margin=20,
                 show_boundary=False, verbose=0):
        """ Initilize the 'PDFcreator' class'.

        Parameters
        ----------
        author: str (mandatory)
            the PDF author.
        client: str (mandatory)
            the client name.
        poweredby: str (mandatory)
            the tool used to produce the results.
        project: str (mandatory)
            the project name.
        timepoint: str (mandatory)
            the project timepoint.
        subject: str (mandatory)
            the subject identifier.
        date: str (mandatory)
            the study date.
        title: str (mandatory)
            a title for the reprot.
        filename: str (mandatory)
            the path to file that will be generated.
        pagesize: 2-uplet (optional, default None)
            the size of the report page.
        *_margin: float (optional, default 0.5)
            the margin expressed in mm.
        show_boundary: bool (optional, default False)
            if True show the frame boudaries.
        verbose: int (optional, default 0)
            the verbosity level.
        """
        # Class parameters
        self.styles = getSampleStyleSheet()
        self.story = []
        self.spacer = Spacer(0, 3 * mm)
        self.verbose = verbose
        self.title = title
        self.author = author
        self.subject = subject
        self.timepoint = timepoint
        self.client = client
        self.poweredby = poweredby
        self.project = project
        self.date = date

        # Create the document template
        self.pagesize = pagesize or letter
        self.left_margin = left_margin * mm
        self.right_margin = right_margin * mm
        self.top_margin = top_margin * mm
        self.bottom_margin = bottom_margin * mm
        self.doc = BaseDocTemplate(
            filename,
            pagesize=self.pagesize,
            showBoundary=int(show_boundary),
            leftMargin=self.left_margin,
            rightMargin=self.right_margin,
            topMargin=self.top_margin,
            bottomMargin=self.bottom_margin,
            title="{0} ({1}-{2})".format(project, subject, timepoint),
            author=author,
            subject=subject)

        # Define the document frames
        # > normal one column frame
        frame1 = Frame(self.doc.leftMargin, self.doc.bottomMargin,
                       self.doc.width, self.doc.height, id="normal")
        # > two columns frame
        frame2 = Frame(self.doc.leftMargin, self.doc.bottomMargin,
                       self.doc.width / 2 - 6, self.doc.height, id="2col1")
        frame3 = Frame(self.doc.leftMargin + self.doc.width / 2 + 6,
                       self.doc.bottomMargin, self.doc.width / 2 - 6,
                       self.doc.height, id="2col2")
        # > landscape one colums frame
        frame4 = Frame(self.doc.leftMargin, self.doc.bottomMargin,
                       self.doc.height, self.doc.width, id="normal")
        # > update document templates
        self.doc.addPageTemplates([
            PageTemplate(id="OneCol", frames=frame1,
                         onPage=header_and_footer),
            PageTemplate(id="OneColLandscape", frames=frame4,
                         onPage=header_and_footer,
                         pagesize=landscape(self.pagesize)),
            PageTemplate(id="TwoCol", frames=[frame2, frame3],
                         onPage=header_and_footer)])

        # Define template parameters
        self.templates = {
            "OneCol": {
                "pagesize": (frame1._aW, frame1._aH - 20),
                "colcount": 1,
                "text_width": self.doc.width,
                "landscape": False
            },
            "OneColLandscape": {
                "pagesize": (frame4._aW + 50, frame4._aH - 20 - 60),
                "colcount": 1,
                "text_width": self.doc.height,
                "landscape": True
            },
            "TwoCol": {
                "pagesize": (frame2._aW, frame2._aH - 20),
                "colcount": 2,
                "text_width": self.doc.width,
                "landscape": False
            }
        }

    def cover(self):
        """ Display a cover.
        """
        # Define a style for the cover
        cover = ParagraphStyle("Cover")
        cover.textColor = "black"
        cover.borderColor = "black"
        cover.borderPadding = 80
        cover.borderWidth = 1
        cover.alignment = TA_CENTER
        cover.fontSize = 30
        cover.borderRadius = 20
        cover.backColor = "gray"
        cover.leading = 40
        pagesize = self.templates["OneCol"]["pagesize"]
        self.story.append(Cover(pagesize[0], pagesize[1] / 3, self.author,
                                self.client, self.poweredby, self.project,
                                self.timepoint, self.subject, self.date))
        self.story.append(Spacer(0, pagesize[1] / 2))
        self.story.append(Paragraph(self.title, cover))

    def triplanar(self, triplanars, page_type="OneCol",
                  preserve_aspect_ratio=True, text_top_margin=0.2,
                  text_padding=0.05, texts=None, linecount=42):
        """ Create a triplanar page with custom layout.

        Parameters
        ----------
        triplanars: list of (4-uplet) or (1-uplet)
            the images to be displayed in triplanar views. The 4-uplet must
            be of the form (image_upper_left, image_upper_right,
            image_bottom_left, image_bottom_right). If a 1-uplet is specified
            display the image in single mode.
        page_type: str (optional, default 'OneCol')
            the page style in 'OneCol', 'TwoCol' or 'OneColLandscape'.
        preserve_aspect_ratio: bool (optional, default True)
            if True preserve the image aspect ratios.
        text_top_margin: float (optional, default 0.2)
            the text margin ratio (ie the height of the text section in the
            page) in [0, 1].
        text_padding: float (optional, default 0.05)
            the text padding ratio (ie the width between text boxes in the
            page) in [0, 1].
        texts: list of str (optional, default None)
            the texts to be displayed in the page.
        linecount: int (optional, default 42)
            the number of characters in each line.
        """
        # Welcome message
        if self.verbose > 0:
            print("[info] Creating a new triplanar page...")

        # Define the page layout
        if page_type in self.templates:
            page_style = self.templates[page_type]
        else:
            raise ValueError("Unexpected '{0}' page type.".format(page_type))
        pagesize = page_style["pagesize"]
        spacer_height = self.spacer.height / mm
        figcount = len(triplanars)
        texts = texts or []
        textcount = len(texts)
        text_padding = page_style["text_width"] * text_padding
        text_width = ((page_style["text_width"] - text_padding *
                      (textcount - 1)) / textcount if textcount > 0 else 0)
        text_height = pagesize[1] * text_top_margin if textcount > 0 else 0
        rowcount = int(math.ceil(figcount / page_style["colcount"]))
        fig_height = ((pagesize[1] - text_height - rowcount * spacer_height) /
                      rowcount)
        text_spacer = Spacer(0, text_height)
        if self.verbose > 0:
            print("[info] #fig {0} - #row {1} - #col {2}.".format(
                figcount, rowcount, page_style["colcount"]))
            print("[info] #txt {0} - #row 1 - #col {0}.".format(
                textcount))
            print("[info] #height {0} - #txt {1} - #fig {2} - "
                  "#figs {3}.".format(pagesize[1], text_height, fig_height,
                                      (fig_height + spacer_height) * rowcount))
            print("[info] #width {0} - #txt {1} - #pad {2}, #tot {3}.".format(
                pagesize[0], text_width, text_padding,
                text_width * textcount + text_padding * (textcount - 1)))

        # Display content
        # > apply page template
        self.story.append(NextPageTemplate(page_type))
        self.story.append(PageBreak())
        if page_style["landscape"]:
            self.story.append(Spacer(0, 60))
        # > set the text
        if textcount > 0:
            if self.verbose > 0:
                print("[info] Insert a text spacer {0}...".format(text_height))
            self.story.append(
                Text(text_height, text_width, text_padding, texts,
                     linecount=linecount, verbose=self.verbose))
            if self.verbose > 0:
                print("[info] Insert a spacer {0}...".format(spacer_height))
            self.story.append(self.spacer)
        # > set the figures
        for cnt, images in enumerate(triplanars, start=1):
            if self.verbose > 0:
                print("[info] Insert a figure {0}...".format(fig_height))
            self.story.append(
                TriPlanar(pagesize[0], fig_height, images,
                          preserve_aspect_ratio=preserve_aspect_ratio))
            if cnt % rowcount != 0:
                if self.verbose > 0:
                    print("[info] Insert a spacer {0}...".format(
                        spacer_height))
                self.story.append(self.spacer)
            elif textcount > 0:
                index = int(cnt / rowcount)
                if index < page_style["colcount"]:
                    if self.verbose > 0:
                        print("[info] Insert a text spacer {0}...".format(
                            text_height))
                    self.story.append(text_spacer)
                    self.story.append(self.spacer)

    def update(self):
        """ Start the construction of the PDF.
        """
        self.doc.build(self.story)


class Cover(Flowable):
    """ Display a cover page.
    """
    def __init__(self, width, height, author, client, poweredby, project,
                 timepoint, subject, date, linespace=14):
        """ Initialize the 'Intro' class.

        Parameters
        ----------
        width: float (mandatory)
            the element width.
        height: float (mandatory)
            the element height.
        author: str (mandatory)
            the author name.
        client: str (mandatory)
            the client name.
        poweredby: str (mandatory)
            the tool used to produce the results.
        project: str (mandatory)
            the project name.
        timepoint: str (mandatory)
            the project timepoint.
        subject: str (mandatory)
            the subject identifier.
        date: str (mandatory)
            the study date.
        linespace: int (mandatory)
            the space between lines.
        """
        Flowable.__init__(self)
        self.width = width
        self.linespace = linespace
        self.left = [
            "Performed by: {0}".format(author),
            "Client: {0}".format(client),
            "Powered by: {0}".format(poweredby)
        ]
        self.right = [
            "Project: {0}".format(project),
            "Subject: {0}".format(subject),
            "Time step: {0}".format(timepoint),
            "QC date: {0}".format(date)
        ]

    def draw(self):
        """ Draw the triplanar element.
        """
        height = self.height - self.linespace
        for row in self.left:
            self.canv.drawString(0, height, row)
            height -= self.linespace
        height = self.height - self.linespace
        for row in self.right:
            self.canv.drawString(3 * self.width / 4, height, row)
            height -= self.linespace


class Text(Flowable):
    """ Display an introduction paragraph.
    """
    def __init__(self, height, text_width, text_padding, texts,
                 linecount=42, linespace=14, verbose=0):
        """ Initialize the 'Intro' class.

        Parameters
        ----------
        height: float (mandatory)
            the text box height.
        text_width: float (mandatory)
            each text box width.
        text_padding: float (mandatory)
            the padding between each text box.
        texts: list of str (mandatory)
            the texts to be displayed.
        linecount: int (optional, default 42)
            the number of characters in each line.
        linespace: int (optional, default 14)
            the space between lines.
        verbose: int (optional, default 0)
            the verbosity level.
        """
        Flowable.__init__(self)
        self.height = height
        self.text_width = text_width
        self.text_padding = text_padding
        self.texts = []
        for txt in texts:
            self.texts.append([txt[i: i + linecount]
                               for i in range(0, len(txt), linecount)])
        self.linespace = linespace
        self.verbose = verbose

    def draw(self):
        """ Draw the text elements.
        """
        for cnt, txt in enumerate(self.texts):
            start_width = (self.text_width + self.text_padding) * cnt
            if self.verbose > 0:
                print("[info] Insert a text {0}-{1}...".format(
                    start_width, self.height))
            height = self.height - self.linespace
            for row in txt:
                self.canv.drawString(start_width, height, row)
                height -= self.linespace
            self.canv.line(start_width, 0, start_width + self.text_width, 0)


class TriPlanar(Flowable):
    """ Display a triplanar view.
    """
    def __init__(self, width, height, images, preserve_aspect_ratio=True):
        """ Initialize the 'TriPlanar' class.

        If a None image is passed, an empty box will be displayed.

        Parameters
        ----------
        width: float (mandatory)
            the element width.
        heights: float (mandatory)
            the element height.
        images: 4-uplet or 1-uplet (mandatory)
            the path to the images to be displayed. If a 4-uplet is specified
            the display order is (image_upper_left, image_upper_right,
            image_bottom_left, image_bottom_right)
        preserve_aspect_ratio: bool (optional, default True)
            if True preserve the image aspect ratios.
        """
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.display_mode = "multi"
        if len(images) == 1:
            self.display_mode = "single"
        self.images = images
        self.preserve_aspect_ratio = preserve_aspect_ratio
        self.missing_file = os.path.join(os.path.dirname(__file__),
                                         "resources", "missing.png")

    def draw(self):
        """ Draw the triplanar element.
        """
        # Check that all expected images exist
        for cnt, path in enumerate(self.images):
            if path is not None and not os.path.isfile(path):
                self.images[cnt] = self.missing_file

        # Dispaly images
        if self.display_mode == "multi":
            if self.images[0] is not None:
                self.canv.drawImage(
                    self.images[0], 0, self.height / 2,
                    width=self.width / 2, height=self.height / 2,
                    preserveAspectRatio=self.preserve_aspect_ratio)
            if self.images[1] is not None:
                self.canv.drawImage(
                    self.images[1], 0, 0,
                    width=self.width / 2, height=self.height / 2,
                    preserveAspectRatio=self.preserve_aspect_ratio)
            if self.images[2] is not None:
                self.canv.drawImage(
                    self.images[2], self.width / 2, self.height / 2,
                    width=self.width / 2, height=self.height / 2,
                    preserveAspectRatio=self.preserve_aspect_ratio)
            if self.images[3] is not None:
                self.canv.drawImage(
                    self.images[3], self.width / 2, 0,
                    width=self.width / 2, height=self.height / 2,
                    preserveAspectRatio=self.preserve_aspect_ratio)
        elif self.display_mode == "single":
            if self.images[0] is not None:
                self.canv.drawImage(
                    self.images[0], 0, 0, width=self.width, height=self.height,
                    preserveAspectRatio=self.preserve_aspect_ratio)


def load_pdf_struct(datapath, struct_file):
    """ Load the the pdf structure.

    The expected pdf description is as follows:

    ::

        pdf_struct = {
            "page1": {
                "images": [
                    relative_path1,
                    relative_path2,
                    relative_path3,
                    [relative_path41, relative_path42, relative_path43,
                     relative_path44]
                ],
                "texts": [
                    "my text 1",
                    "my text 2"
                ],
                "type": "Triplanar",
                "top_margin": 42,
                "linecount": 100,
                "style": "OneCol"
            },
            ...
        }

    Parameters
    ----------
    datapath: str (mandatory)
        the path where the images are stored: used to complete the relative
        path.
    struct_file: str (mandatory)
        the path to the pdf description.

    Retruns
    -------
    pdf_struct: dict
        the pdf structure.
    """
    # Load the structure
    with open(struct_file) as open_file:
        pdf_struct = json.load(open_file, object_pairs_hook=OrderedDict)

    # Update the image relative path
    for name, struct in pdf_struct.items():
        if "images" in struct:
            struct["images"] = update_path(datapath, struct["images"])

    return pdf_struct


def update_path(datapath, listpath):
    """ Update the path of a recusrsive list structure.

    Parameters
    ----------
    datapath: str (mandatory)
        the path where the images are stored: used to complete the relative
        path.
    listpath: list (mandatory)
        a recursive list with relative path.

    Returns
    -------
    newlist: list
        a recursive list with absolute path.
    """
    newlist = []
    for rpath in listpath:
        if isinstance(rpath, list):
            newlist.append(update_path(datapath, rpath))
        elif rpath is None:
            newlist.append(rpath)
        else:
            newlist.append(os.path.join(datapath, rpath))
    return newlist


def generate_pdf(datapath, struct_file, author, client, poweredby, project,
                 timepoint, subject, date, title, filename, pagesize=None,
                 left_margin=10, right_margin=10, top_margin=20,
                 bottom_margin=20, show_boundary=False, verbose=1):
    """ Generate a PDF report from a description file.

    Parameters
    ----------
    datapath: str (mandatory)
        the path where the images are stored: used to complete the relative
        path.
    struct_file: str (mandatory)
        the path to the pdf description.
    author: str (mandatory)
        the author name.
    client: str (mandatory)
        the client name.
    poweredby: str (mandatory)
        the tool used to produce the results.
    project: str (mandatory)
        the project name.
    timepoint: str (mandatory)
        the project timepoint.
    subject: str (mandatory)
        the subject identifier.
    date: str (mandatory)
        the study date.
    title: str (mandatory)
        a title for the report.
    filename: str (mandatory)
        the path to file that will be generated.
    pagesize: 2-uplet (optional, default None)
        the size of the report page.
    *_margin: float (optional, default 0.5)
        the margin expressed in mm.
    show_boundary: bool (optional, default False)
        if True show the frame boudaries.
    verbose: int (optional, default 0)
        the verbosity level.
    """
    # Load the pdf structure in memory
    pdf_struct = load_pdf_struct(datapath, struct_file)

    # Create the pdf page
    creator = PDFcreator(author, client, poweredby, project, timepoint,
                         subject, date, title, filename, pagesize=pagesize,
                         left_margin=left_margin, right_margin=right_margin,
                         top_margin=top_margin, bottom_margin=bottom_margin,
                         show_boundary=show_boundary, verbose=verbose)

    # Add item to the pdf page
    for name, struct in pdf_struct.items():
        if struct["type"] == "cover":
            creator.cover()
        elif struct["type"] == "triplanar":
            creator.triplanar(
                struct["images"],
                page_type=struct["style"],
                text_top_margin=struct["topmargin"],
                linecount=struct.get("linecount", 0),
                texts=struct.get("texts", None))
        else:
            raise ValueError("Unexpected '{0}' page type.".format(
                struct["type"]))

    # Save the page to disk
    creator.update()
