"""Render styled Rex HTML captures to a MP4 and looping GIF.
Dependencies: pillow, imageio-ffmpeg. Set DEMO_FONT to a monospace TTF.
"""
from html.parser import HTMLParser
from pathlib import Path
import json,re,os
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parent
fontpath=os.environ['DEMO_FONT']
font=ImageFont.truetype(fontpath,22)
CW=font.getlength('M'); LH=27
class Capture(HTMLParser):
    def __init__(self,draw):super().__init__();self.draw=draw;self.styles=[];self.x=0;self.y=0
    def handle_starttag(self,tag,attrs):
        if tag!='div':return
        style=dict(attrs).get('style','')
        def color(name,default):
            m=re.search(r'(?:^|;)\s*'+name+r':\s*rgb\((\d+),\s*(\d+),\s*(\d+)\)',style)
            return tuple(map(int,m.groups())) if m else default
        self.styles.append((color('color',(188,188,188)),color('background-color',(28,28,28))))
    def handle_endtag(self,tag):
        if tag=='div' and self.styles:self.styles.pop()
    def handle_data(self,data):
        fg,bg=self.styles[-1] if self.styles else ((188,188,188),(28,28,28))
        for i,line in enumerate(data.split('\n')):
            if i:self.y+=LH;self.x=0
            if line:
                x=64+self.x; y=48+self.y;w=CW*len(line)
                self.draw.rectangle((x,y,x+w,y+LH),fill=bg)
                self.draw.text((x,y),line,font=font,fill=fg)
                self.x+=w
scenes=json.loads((ROOT/'scenes.json').read_text());frames=[]
for idx,s in enumerate(scenes):
    im=Image.new('RGB',(1200,768),'#1c1c1c');d=ImageDraw.Draw(im)
    Capture(d).feed((ROOT/'captures'/s['file']).read_text().rstrip('\n'))
    frames.append((im,s['seconds']))
frames[8][0].save(ROOT/'poster.png')
writer=imageio_ffmpeg.write_frames(str(ROOT/'slop-demo.mp4'),(1200,768),fps=12,codec='libx264',output_params=['-crf','20','-movflags','+faststart'])
writer.send(None)
for im,seconds in frames:
    for _ in range(seconds*12):writer.send(im.tobytes())
writer.close()
gif=[im.resize((960,614)).quantize(colors=128) for im,_ in frames]
gif[0].save(ROOT/'slop-demo.gif',save_all=True,append_images=gif[1:],duration=[s*1000 for _,s in frames],loop=0,optimize=False)
print('Rendered MP4 and GIF:',sum(s for _,s in frames),'seconds')
