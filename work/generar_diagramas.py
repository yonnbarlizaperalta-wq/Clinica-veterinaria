from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'docs'
OUT.mkdir(exist_ok=True)
NAVY=HexColor('#17324D'); TEAL=HexColor('#147D79'); BG=HexColor('#F4F7FA'); INK=HexColor('#243746'); LINE=HexColor('#8194A5'); PALE=HexColor('#E8F4F3'); GOLD=HexColor('#FFF2D8')

def rounded(c,x,y,w,h,fill=white,stroke=LINE,r=9):
    c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(1.1); c.roundRect(x,y,w,h,r,fill=1,stroke=1)

def fit(c, text, x, y, maxw, size=9):
    c.setFont('Helvetica', size)
    if stringWidth(text,'Helvetica',size)>maxw:
        while text and stringWidth(text+'…','Helvetica',size)>maxw: text=text[:-1]
        text += '…'
    c.drawString(x,y,text)

def arrow(c,x1,y1,x2,y2,color=LINE):
    import math
    c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(1.0); c.line(x1,y1,x2,y2)
    a=math.atan2(y2-y1,x2-x1); size=5
    p=c.beginPath(); p.moveTo(x2,y2); p.lineTo(x2-size*math.cos(a-.45),y2-size*math.sin(a-.45)); p.lineTo(x2-size*math.cos(a+.45),y2-size*math.sin(a+.45)); p.close()
    c.drawPath(p,fill=1,stroke=0)

def usecases():
    f=OUT/'diagrama_actores.pdf'; c=canvas.Canvas(str(f),pagesize=(1000,650))
    c.setFillColor(BG); c.rect(0,0,1000,650,fill=1,stroke=0)
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold',22); c.drawString(40,608,'Clínica veterinaria Huellitas')
    c.setFillColor(TEAL); c.setFont('Helvetica',11); c.drawString(40,588,'Diagrama de casos de uso · Actores y responsabilidades')
    sx,sy,sw,sh=255,78,700,475
    c.setStrokeColor(TEAL); c.setLineWidth(1.5); c.roundRect(sx,sy,sw,sh,14,fill=0,stroke=1)
    c.setFillColor(TEAL); c.roundRect(sx+18,sy+sh-29,205,22,7,fill=1,stroke=0)
    c.setFillColor(white); c.setFont('Helvetica-Bold',10); c.drawString(sx+30,sy+sh-22,'Sistema de clínica veterinaria')
    # Actors and per-role use cases
    roles=[('Administrador',['Gestionar usuarios','Gestionar veterinarios','Consultar reportes']),('Recepcionista',['Registrar propietario','Registrar mascota','Agendar cita']),('Veterinario',['Consultar historia clínica','Registrar consulta','Registrar vacunación'])]
    ys=[435,310,185]
    # Usecase coordinates; each actor connects to 3
    uses=[[(470,450),(690,450),(470,390)],[(470,325),(690,325),(470,265)],[(470,200),(690,200),(470,140)]]
    for (role,labels), ay, pts in zip(roles,ys,uses):
        # stick actor
        c.setStrokeColor(INK); c.setLineWidth(1.5); c.circle(92,ay+25,11,fill=0,stroke=1); c.line(92,ay+14,92,ay-20); c.line(92,ay+4,72,ay-5); c.line(92,ay+4,112,ay-5); c.line(92,ay-20,76,ay-42); c.line(92,ay-20,108,ay-42)
        c.setFillColor(INK); c.setFont('Helvetica-Bold',10); c.drawCentredString(92,ay-57,role)
        for label,(ux,uy) in zip(labels,pts):
            # actor line ends at ellipse boundary; keep each association legible
            arrow(c,115,ay,ux-74,uy,LINE)
            c.setFillColor(PALE); c.setStrokeColor(TEAL); c.setLineWidth(1); c.ellipse(ux-78,uy-18,ux+78,uy+18,fill=1,stroke=1)
            c.setFillColor(INK); c.setFont('Helvetica',9); c.drawCentredString(ux,uy-3,label)
    c.setFillColor(INK); c.setFont('Helvetica-Oblique',8); c.drawRightString(950,43,'Relaciones directas entre actores y casos de uso')
    c.save()

def er():
    f=OUT/'diagrama_er.pdf'; c=canvas.Canvas(str(f),pagesize=(1200,850))
    c.setFillColor(BG); c.rect(0,0,1200,850,fill=1,stroke=0)
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold',22); c.drawString(38,808,'Clínica veterinaria Huellitas · Modelo entidad-relación')
    c.setFillColor(TEAL); c.setFont('Helvetica',10); c.drawString(38,789,'PK llave primaria · FK llave foránea · UNIQUE valores únicos · Cardinalidades en los extremos')
    # x,y,w, fields per table
    tables={
      'tbl_propietario':(35,565,250,['PK propietario_id BIGINT','nombres VARCHAR(80)','apellidos VARCHAR(80)','documento VARCHAR(20) UNIQUE','telefono VARCHAR(20)','correo VARCHAR(254)','direccion VARCHAR(160)']),
      'tbl_mascota':(355,565,250,['PK mascota_id BIGINT','FK propietario_id BIGINT','nombre VARCHAR(80)','especie VARCHAR(40)','raza VARCHAR(60)','sexo VARCHAR(10)','fecha_nacimiento DATE NULL','peso_kg DECIMAL(6,2)','activo BOOLEAN']),
      'tbl_historia_clinica':(675,565,250,['PK historia_id BIGINT','FK mascota_id BIGINT UNIQUE','fecha_apertura DATE','alergias TEXT','antecedentes TEXT','observaciones TEXT']),
      'tbl_veterinario':(945,565,220,['PK veterinario_id BIGINT','nombres VARCHAR(80)','apellidos VARCHAR(80)','documento VARCHAR(20) UNIQUE','tarjeta_profesional VARCHAR(40) UNIQUE','telefono VARCHAR(20)','correo VARCHAR(254) UNIQUE','especialidad VARCHAR(80)','activo BOOLEAN']),
      'tbl_cita':(35,180,250,['PK cita_id BIGINT','FK mascota_id BIGINT','FK veterinario_id BIGINT','fecha_hora DATETIME','motivo VARCHAR(180)','estado VARCHAR(12)','notas TEXT']),
      'tbl_vacuna':(355,180,250,['PK vacuna_id BIGINT','nombre VARCHAR(100) UNIQUE','especie_objetivo VARCHAR(40)','fabricante VARCHAR(100)','intervalo_meses SMALLINT','descripcion TEXT','activa BOOLEAN']),
      'tbl_aplicacion_vacuna':(675,180,250,['PK aplicacion_id BIGINT','FK mascota_id BIGINT','FK vacuna_id BIGINT','FK veterinario_id BIGINT','fecha DATE','dosis VARCHAR(40)','lote VARCHAR(60)','proxima_fecha DATE NULL','UNIQUE(mascota, vacuna, fecha)']),
    }
    positions={}
    for name,(x,y,w,fields) in tables.items():
        h=32+len(fields)*17; positions[name]=(x,y,w,h)
        rounded(c,x,y,w,h,white,TEAL,7)
        c.setFillColor(NAVY); c.roundRect(x,y+h-27,w,27,7,fill=1,stroke=0); c.rect(x,y+h-27,w,8,fill=1,stroke=0)
        c.setFillColor(white); c.setFont('Helvetica-Bold',10); c.drawString(x+10,y+h-18,name)
        for i,field in enumerate(fields):
            yy=y+h-43-i*17
            if field.startswith('PK'): c.setFillColor(TEAL)
            elif field.startswith('FK'): c.setFillColor(HexColor('#8A5A00'))
            else: c.setFillColor(INK)
            c.setFont('Helvetica-Bold' if field.startswith(('PK','FK')) else 'Helvetica',8)
            fit(c,field,x+10,yy,w-20,8)
    # connect edges at boundaries; labels clarify cardinality
    relationships=[((285,680),(355,680),'1','N','tiene'),((605,680),(675,680),'1','1','registra'),((160,565),(160,287),'1','N','agenda'),((485,565),(200,287),'1','N','atiende'),((430,565),(800,468),'1','N','recibe'),((605,365),(675,365),'1','N','incluye'),((925,240),(1010,565),'N','1','aplica')]
    for (a,b,ca,cb,label) in relationships:
        # Orthogonal direct connectors (some are diagonal where space is limited).
        arrow(c,*a,*b,LINE)
        c.setFillColor(NAVY); c.setFont('Helvetica-Bold',8); c.drawCentredString((a[0]+b[0])/2,(a[1]+b[1])/2+7,f'{ca} — {label} — {cb}')
    # explicit N:M note
    rounded(c,955,180,210,118,GOLD,HexColor('#D7A848'),7)
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold',10); c.drawString(968,278,'Relación N:M resuelta')
    c.setFillColor(INK); c.setFont('Helvetica',9)
    for i,t in enumerate(['Mascota N:M Vacuna mediante','tbl_aplicacion_vacuna. La entidad','guarda fecha, dosis, lote y próxima','aplicación; se evita repetir la misma','vacuna para la mascota en una fecha.']): c.drawString(968,259-i*15,t)
    c.setFillColor(INK); c.setFont('Helvetica-Oblique',8); c.drawString(38,115,'Entidad débil: tbl_historia_clinica depende de tbl_mascota (relación 1:1, FK única).')
    c.drawString(38,99,'Relaciones: Propietario 1:N Mascota · Veterinario 1:N Cita · Mascota/Vacuna N:M Aplicación de vacuna.')
    c.save()

usecases(); er()
