"""Original demonstration text, dedicated to the public domain under CC0."""
from pathlib import Path
from reportlab.pdfgen import canvas
import zipfile
p=Path(__file__).parent
c=canvas.Canvas(str(p/'A-small-reading-experiment.pdf')); c.setTitle('A small reading experiment')
for title,lines in [('Chapter 1: Questions first',['Reading is not only collecting sentences. It is a conversation with an idea.','A useful question makes a hidden assumption visible.','Try selecting this sentence and ask: What assumption is being made?']),('Chapter 2: Changing your mind',['An initial question is a starting point, not a conclusion.','As evidence accumulates, append a new insight rather than erase the old question.','This preserves the path from uncertainty to understanding.'])]:
 c.setFont('Helvetica-Bold',20);c.drawString(60,770,title);c.setFont('Helvetica',12)
 for i,line in enumerate(lines): c.drawString(60,720-i*30,line)
 c.setFont('Helvetica',9);c.drawString(60,60,'Original prototype sample. CC0 1.0. No third-party copyrighted text.');c.showPage()
c.save()
with zipfile.ZipFile(p/'带着问题读书.epub','w') as z:
 z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
 z.writestr('META-INF/container.xml','<?xml version="1.0"?><container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
 z.writestr('OEBPS/content.opf','''<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bookid">urn:uuid:reading-demo</dc:identifier><dc:title>带着问题读书</dc:title><dc:language>zh-CN</dc:language><meta property="dcterms:modified">2026-11-03T00:00:00Z</meta></metadata><manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="c1" href="chapter1.xhtml" media-type="application/xhtml+xml"/><item id="c2" href="chapter2.xhtml" media-type="application/xhtml+xml"/></manifest><spine><itemref idref="c1"/><itemref idref="c2"/></spine></package>''')
 z.writestr('OEBPS/nav.xhtml','<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>目录</title></head><body><nav epub:type="toc"><ol><li><a href="chapter1.xhtml">从问题开始</a></li><li><a href="chapter2.xhtml">保留思考的轨迹</a></li></ol></nav></body></html>')
 for n,title,text in [(1,'从问题开始','阅读不只是收集句子，而是与一个观点展开对话。一个好的问题，会让隐藏的前提浮出水面。\n试着选中这段话，问一问：作者默认了什么？📖 每一个问题都值得保留。'),(2,'保留思考的轨迹','最初的问题只是起点，不是终点。随着证据增加，我们可以追加新的理解，而不必抹去最初的困惑。\n这样，笔记保存的不只是结论，还有走向结论的过程。')]:
  z.writestr(f'OEBPS/chapter{n}.xhtml',f'<html xmlns="http://www.w3.org/1999/xhtml"><head><title>{title}</title></head><body><h1>{title}</h1><p>{text}</p><p>本试读文本为原型原创，采用 CC0 1.0 公共领域贡献。</p></body></html>')
