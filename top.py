from datetime import date,datetime,timedelta
import sqlite3
from flask import Flask,render_template,redirect,url_for,session,logging,request,flash
from wtforms import Form,StringField,PasswordField,validators,IntegerField,DateField
from passlib.hash import sha256_crypt
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


now = datetime.now()
today = date.today()




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/HP/Desktop/flask-blog/toplama/toplama.db'
db = SQLAlchemy(app)


#Kullanıcı giriş decoratir
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        if "logged_in" in session:
            #cursor = mysql.connection.cursor()

            #sorgu = "select * from users where kullanıci_adi = %s"

            #result = cursor.execute(sorgu,(session["username"],)) 

            #data = cursor.fetchone()
            #yetki = data["yetki"]
            
            result = users.query.filter_by(kullanıci_adi = session["username"]).first()      
            
            if result.yetki == "Finans":
                return f(*args, **kwargs)
            else:
                return redirect(url_for("sahatop"))
        else:
            flash("Bu Sayfayı Görüntülemek için Giriş Yapınız...","danger")
            return redirect(url_for('login', next=request.url))
        
    return decorated_function

#Toplama Formu
class ToplamaForm(Form):
    miktar = IntegerField('Miktar',validators=[validators.length(min = 3,max = 9)])
    kimden = StringField("Buraya Select gelecek")
    session = StringField("buraya session gelecek")
    

class ToplamafinForm(Form):
    miktar = IntegerField('Miktar',validators=[validators.length(min = 3,max = 9)])
    kimden = StringField("Teslim Eden")
    session = StringField("Teslim Alan")
    info = StringField("Açıklama Giriniz")



#User Formu
class registerForm(Form):
    username = StringField("Kullanıcı Adı :", validators=[validators.length(min=3,max=10),validators.data_required(message="Lütfen Kullanıcı Adı Giriniz. ")])
    grup = StringField("Grup :")
    yetki = StringField("Yetki :")
    password = PasswordField("Şifre : ",validators=[
        validators.data_required(message="Lütfen Şifre Giriniz...")])

#User güncelleme Formu
class registerGForm(Form):
    
    grup = StringField("Grup :")
    yetki = StringField("Yetki :")
    password = PasswordField("Şifre : ")

#giriş Formu
class LoginForm(Form):
    username = StringField("Kullanıcı Adı: ")
    password = PasswordField("Parola")

#datefield deneme
class datefield(Form):
    ara = StringField("Ara...")
    date = DateField(
        "", format='%Y-%m-%d',
        default=date.today(),
        validators=[validators.DataRequired()])

#grup form
class grupform(Form):
    grup = StringField("Grup Adını Giriniz...")




#app =  Flask(__name__)

app.secret_key = "toplama"
#app.config["MYSQL_HOST"] = "localhost"
#app.config["MYSQL_USER"] = "root"
#app.config["MYSQL_PASSWORD"] = "551921"
#app.config["MYSQL_DB"] = "toplama"
#app.config["MYSQL_CURSORCLASS"] = "DictCursor"

#mysql = MySQL(app)




@app.route("/")
@login_required
def index():   
    return render_template("index.html")


@app.route("/toplama", methods = ["GET","POST"])
@login_required
def toplama():
    form = datefield(request.form)
    if request.method == "GET":

        #cursor = mysql.connection.cursor()


        #sorgu = "select * from toplama where tarih >= DATE(NOW())"

        #result = cursor.execute(sorgu)

        date1 = date.today()

        result = toplama.query.filter(toplama.tarih >= date1).all()

        if result:          
            data = toplama.query.filter(toplama.tarih >= date1).all()
            return render_template("toplama.html",data = data,form = form)
        else: 
            return render_template("toplama.html",form = form)
    else:
        keyword = request.form.get("keyword")
        date1 = form.date.data
        date2 = date1 + timedelta(days=1)
        # cursor = mysql.connection.cursor()

        # sorgu = "select * from toplama where date(tarih) = %s and concat(alan,veren) like '%" + "%" + keyword + "%" + "%' "
        # result = cursor.execute(sorgu,(date,))
        result = db.session.query(toplama).filter(toplama.alan.like('%' + keyword + '%'),toplama.tarih >= date1,toplama.tarih <= date2).all()
        if not result:
            flash("Aramaya uygun işlem yok ","warning")
            return render_template("toplama.html",form = form)
        else:
            data = db.session.query(toplama).filter(toplama.alan.like('%' + keyword + '%'),toplama.tarih >= date1,toplama.tarih <= date2).all()
            return render_template("toplama.html",data = data,form = form)





@app.route('/login',methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data

        result = users.query.filter_by(kullanıci_adi=username).first()

        if result:
            data = users.query.filter_by(kullanıci_adi = username).first()
            real_password = data.password
            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarıyla Giriş Yapıldı..","success")

                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("index"))
            else:
                flash("Paralınızı Yanlış Girdiniz...","danger")
                return redirect(url_for("login"))
        else:
            flash("Lütfen Geçerli Bir Kullanıcı Adı Giriniz.","danger")
            return redirect(url_for("login"))
    else:
        return render_template("login.html",form = form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/saha_op')
@login_required
def saha_op():
    #cursor = mysql.connection.cursor()

    #sorgu = "select * from users"

    #result = cursor.execute(sorgu)

    result = users.query.all()

    if result:
        data = users.query.all()
        return render_template("saha_op.html",data = data)
    else: 
        return render_template("saha_op.html")
    

@app.route('/saha_op_ekle',methods = ["GET","POST"])
@login_required
def saha_opp_ekle():
    form = registerForm(request.form)

    #cursor = mysql.connection.cursor()

    #sorgu1 = "select * from grup"
    #sorgu2 = "select * from yetki"

    #cursor.execute(sorgu1)
    #result = cursor.fetchall()
    #cursor.execute(sorgu2)
    #result2 = cursor.fetchall()
    
    result = db_grup.query.all()
    result2 = db_yetki.query.all()

    if request.method == "POST" and form.validate:
        kullanıci_adi = form.username.data
        grup = request.form.get("grup")
        yetki = request.form.get("yetki")
        password = sha256_crypt.encrypt(form.password.data)
        
        #cursor = mysql.connection.cursor()

        #sorgu = "Insert into users(kullanıci_adi,grup,yetki,password) VALUES(%s,%s,%s,%s)"

        #cursor.execute(sorgu,(kullanıci_adi,grup,yetki,password))
        #mysql.connection.commit()
        #cursor.close()

        newuser = users(kullanıci_adi = kullanıci_adi,grup = grup,yetki = yetki,password = password)
        db.session.add(newuser)
        db.session.commit()
        flash("İşlemininiz Gerçekleşti","success")

        return redirect(url_for("saha_op"))
    else:

        return render_template("saha_op_ekle.html",form = form,result = result,result2 = result2)


@app.route('/sahatop',methods =["GET","POST"])
def sahatop():
    form = ToplamaForm(request.form)

    # cursor = mysql.connection.cursor()
    # sorgu1 = "select * from users where kullanıci_adi = %s"
    # cursor.execute(sorgu1,(session["username"],))
    # result1 = cursor.fetchone()
    # grup = result1["grup"]
    # sorgu2 = "select * from users where grup = %s"
    # cursor.execute(sorgu2,(grup,))
    # cepciler = cursor.fetchall()

    result1 = users.query.filter_by(kullanıci_adi = session["username"]).first()
    grup = result1.grup
    cepciler = users.query.filter_by(grup = grup).all()

    if request.method == "POST" and form.validate:
        miktar = form.miktar.data
        veren = request.form.get("cepci")
        alan = session["username"]

        # cursor = mysql.connection.cursor()

        # sorgu = "Insert into toplama(miktar,veren,alan) VALUES(%s,%s,%s)"

        # cursor.execute(sorgu,(miktar,veren,alan))
        # mysql.connection.commit()
        # cursor.close()

        newtop = toplama(miktar = miktar, veren = veren,alan = alan,tarih = datetime.now())
        db.session.add(newtop)
        db.session.commit()

        flash("İşlemininiz Gerçekleşti","success")
        return redirect(url_for("sahatop"))
    else:
        # cursor = mysql.connection.cursor()

        # sorgu = "select * from toplama where alan = %s and tarih >= DATE(NOW())"

        # result = cursor.execute(sorgu,(session["username"],))

        #result = toplama.query.filter(toplama.tarih >= today).all()
        result = db.session.query(toplama).filter(toplama.alan == session["username"], toplama.tarih >= date.today()).all()


        if result:
            toplanan = db.session.query(toplama).filter(toplama.alan == session["username"], toplama.tarih >= date.today()).all()
            return render_template("sahatop.html",form = form,toplanan = toplanan,cepciler = cepciler)
        else:
            return render_template("sahatop.html",form = form,cepciler = cepciler)


@app.route('/toplama/delete/<string:id>')
@login_required
def topsil(id):
    # cursor = mysql.connection.cursor()

    # sorgu = "Delete from toplama where id = %s"

    # cursor.execute(sorgu,(id,))   

    # mysql.connection.commit() 

    toplasil = toplama.query.filter_by(id = id).first()
    db.session.delete(toplasil)
    db.session.commit()


    flash("İşlem Başarıyla Silindi...","warning")
    return redirect(url_for("toplama"))

@app.route('/saha_op/delete/<string:id>')
@login_required
def saha_op_sil(id):
    # cursor = mysql.connection.cursor()

    # sorgu = "Delete from users where id = %s"

    # cursor.execute(sorgu,(id,))   

    # mysql.connection.commit() 
    cepsil = users.query.filter_by(id = id).first()
    db.session.delete(cepsil)
    db.session.commit()

    flash("Operatör Başarıyla Silindi...","warning")
    return redirect(url_for("saha_op"))

@app.route('/saha_op/edit/<string:id>', methods = ["GET","POST"])
@login_required
def saha_op_edit(id):
    if request.method == "GET":
        # cursor = mysql.connection.cursor()

        # sorgu = "select * from users where id = %s"
        # result = cursor.execute(sorgu,(id,))

        result = users.query.filter_by(id = id).first()

        if not result:
            flash("Böyle Bir Kullanıcı Yok ...","danger")
            return redirect(url_for("saha_op"))
        else:
            sahaop = users.query.filter_by(id = id).first()
            form = registerGForm()
            
            username = sahaop.kullanıci_adi
            form.grup.data = sahaop.grup
            form.yetki.data = sahaop.yetki
            return render_template("sahaopedit.html",form = form,username = username)
    else:
        form = registerGForm(request.form)

        yenigrup = form.grup.data
        yeniyetki = form.yetki.data
        yenipass = form.password.data
        kriptopass = sha256_crypt.encrypt(form.password.data)


        if yenipass == "":
            # sorgu2 = "Update users Set grup = %s,yetki = %s where id = %s "
            # cursor = mysql.connection.cursor()
            # cursor.execute(sorgu2,(yenigrup,yeniyetki,id))
            # mysql.connection.commit()
            sahaop = users.query.filter_by(id = id).first()
            sahaop.yetki = yeniyetki
            sahaop.grup = yenigrup     
            db.session.commit()

        else:
            # sorgu3 = "Update users Set grup = %s,yetki = %s,password =%s where id = %s"
            # cursor = mysql.connection.cursor()
            # cursor.execute(sorgu3,(yenigrup,yeniyetki,kriptopass,id))
            # mysql.connection.commit()
            sahaop = users.query.filter_by(id = id).first()
            sahaop.yetki = yeniyetki
            sahaop.grup = yenigrup
            sahaop.password = kriptopass     
            db.session.commit()

        flash("Kullanıcı Başarıyla Güncellendi","success")
        return redirect(url_for("saha_op"))

@app.route('/toplama_gir',methods =["GET","POST"])
@login_required
def topekle():
    form = ToplamafinForm(request.form)

    if request.method == "POST" and form.validate:
        miktar = form.miktar.data
        veren = form.kimden.data
        alan = form.session.data
        info = form.info.data

        #cursor = mysql.connection.cursor()

        #sorgu = "Insert into toplama(miktar,veren,alan,info) VALUES(%s,%s,%s,%s)"

        #cursor.execute(sorgu,(miktar,veren,alan,info))
        #mysql.connection.commit()
        #cursor.close()
        
        newtoplama = toplama(miktar = miktar,alan = alan,veren = veren,tarih = datetime.now(),info = info)
        db.session.add(newtoplama)
        db.session.commit()


        flash("İşlemininiz Gerçekleşti","success")
        return redirect(url_for("toplama"))
    else:
         return render_template("toplama_gir.html",form = form)

@app.route('/toplama/edit/<string:id>', methods = ["GET","POST"])
@login_required
def toplama_edit(id):
    if request.method == "GET":
        # cursor = mysql.connection.cursor()

        # sorgu = "select * from toplama where id = %s"
        # result = cursor.execute(sorgu,(id,))
        result = db.session.query(toplama).filter(toplama.id == id).first()

        if not result:
            flash("Böyle Bir toplama Yok ...","danger")
            return redirect(url_for("toplama"))
        else:
            
            form = ToplamafinForm()
            
            toplamaedit = db.session.query(toplama).filter(toplama.id == id).first()

            form.miktar.data = toplamaedit.miktar
            form.kimden.data = toplamaedit.alan
            form.session.data = toplamaedit.veren
            form.info.data = toplamaedit.info
            return render_template("toplamaedit.html",form = form)
    else:
        form = ToplamafinForm(request.form)

        yenimiktar = form.miktar.data
        yenialan = form.kimden.data
        yeniveren = form.session.data
        yeniinfo = form.info.data

        toplamaed = db.session.query(toplama).filter(toplama.id == id).first()
        toplamaed.miktar = yenimiktar
        toplamaed.alan = yenialan
        toplamaed.veren = yeniveren
        toplamaed.info = yeniinfo

        db.session.commit()

        # sorgu2 = "Update toplama Set miktar = %s,alan = %s,veren = %s,info = %s where id = %s "
        # cursor = mysql.connection.cursor()
        # cursor.execute(sorgu2,(yenimiktar,yenialan,yeniveren,yeniinfo,id))
        # mysql.connection.commit()
        

        flash("İşlem Başarıyla Güncellendi","success")
        return redirect(url_for("toplama"))

@app.route("/grup",methods = ["GET","POST"])
@login_required
def grup():
    form = grupform(request.form)

    if request.method == "POST":
        yenigrup = form.grup.data
        # cursor = mysql.connection.cursor()
        # sorgu2 = "Insert into grup(grup) VALUES(%s)"
        # cursor.execute(sorgu2,(yenigrup,))
        # mysql.connection.commit()

        yenidbgrup = db_grup(grup = yenigrup)

        db.session.add(yenidbgrup)
        db.session.commit()



        return redirect(url_for("grup"))
    else:
        # cursor = mysql.connection.cursor()
        # sorgu = "select * from grup"
        # result = cursor.execute(sorgu)

        result = db_grup.query.all()

        if not result:   
            flash("Herhangi bir grup yok")
            return render_template("grup.html",form = form)
        else:      
            gruplar = db_grup.query.all()    
            return render_template("grup.html",form = form,gruplar = gruplar)


class users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    kullanıci_adi = db.Column(db.String)
    grup = db.Column(db.String)
    yetki= db.Column(db.String)
    password = db.Column(db.String)
    
class toplama(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    miktar = db.Column(db.Integer)
    alan = db.Column(db.String)
    veren = db.Column(db.String)
    tarih = db.Column(db.DateTime)
    info = db.Column(db.String)

class db_grup(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    grup = db.Column(db.String)

class db_yetki(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    yetki= db.Column(db.String)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True,host='0.0.0.0',port=5000)

