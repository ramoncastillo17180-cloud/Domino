from pathlib import Path
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.oxml.ns import qn
from docx.enum.text import WD_TAB_ALIGNMENT,WD_TAB_LEADER
p=Path('documentacion/Reporte_Tecnico_Efecto_Domino.docx');d=Document(p)
for tree in [d._element,d.styles.element]:
 for el in tree.iter():
  if el.tag==qn('w:rFonts'):
   el.attrib.clear()
   for k in ['ascii','hAnsi','eastAsia','cs']:el.set(qn('w:'+k),'Arial')
  if el.tag==qn('w:pBdr'):el.getparent().remove(el)
for para in d.paragraphs:
 if para.text.startswith('La referencia de Russell'):
  para._element.getparent().remove(para._element);continue
 if para.style.name in ('Heading 1','Heading 2','Title'):
  for r in para.runs:r.font.name='Arial';r.font.bold=True;r.font.size=Pt(14 if para.style.name!='Heading 2' else 12)
 if para.text.startswith(('Python Software Foundation.','Russell, S. J.')):
  text=para.text;para.clear();para.paragraph_format.left_indent=Cm(1.27);para.paragraph_format.first_line_indent=Cm(-1.27)
  titles=['collections — Container datatypes','time — Time access and conversions','tkinter — Python interface to Tcl/Tk','Artificial intelligence: A modern approach']
  title=next(t for t in titles if t in text);before,after=text.split(title)
  para.add_run(before);para.add_run(title).italic=True;para.add_run(after)
# Índice: números alineados con guías de puntos.
import json
headings=json.loads(Path('documentacion/trabajo/indice_esperado.json').read_text(encoding='utf-8'))
for para in d.paragraphs:
 for title,page,kind in headings:
  if para.text==title+'  '+str(page):
   para.clear();para.paragraph_format.tab_stops.add_tab_stop(Pt(468),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
   r=para.add_run(title+'\t'+str(page));r.font.name='Arial';r.font.size=Pt(10.5)
for sec in d.sections:
 for para in sec.footer.paragraphs:
  for r in para.runs:r.font.size=Pt(9)
d.save(p)
