from flask import Flask, render_template, request, redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_user,logout_user,current_user,UserMixin,login_required
import matplotlib.pyplot as plt
import os


# Harmonizing the world through immersive music discovery and sharing and deliver the best user experience through innovative web services

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
app.config["UPLOAD_FOLDER"] = "static/audio"
app.config["IMAGE_FOLDER"] = "static/images"

app.config["SECRET_KEY"] = "myverysecretkey"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["IMAGE_FOLDER"], exist_ok=True)

db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager(app)
app.app_context().push()

class Admin(db.Model,UserMixin):
    __tablename__ = "admin"
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    def get_id(self):
        return str(self.admin_id)


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(20), nullable=False)


class Artist(db.Model):
    __tablename__ = "artist"
    artist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), nullable=False)
    flag = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), unique=True, nullable=False)


class Genre(db.Model):
    __tablename__ = "genre"
    genre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), nullable=False)


class Album(db.Model):
    __tablename__ = "album"
    album_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    release = db.Column(db.String(15), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.artist_id"), nullable=False)
    flag = db.Column(db.Boolean, default=True)
    artist = db.relationship("Artist", backref="albums")


class Song(db.Model):
    __tablename__ = "song"
    song_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    lyrics = db.Column(db.String, nullable=False)
    image_path = db.Column(db.String(255))
    mp3_path = db.Column(db.String(255))
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.artist_id"), nullable=False)
    artist = db.relationship("Artist", backref="songs", foreign_keys=[artist_id])
    artistname = db.Column(db.String(), db.ForeignKey("artist.name"), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.genre_id"), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey("album.album_id"), nullable=False)
    rating = db.Column(db.Integer, default=0)
    flag = db.Column(db.Boolean, default=True)
    release = db.Column(db.String(15), nullable=False)
    duration = db.Column(db.Float, nullable=False)


class Playlist(db.Model):
    __tablename__ = "playlist"
    playlist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    user = db.relationship("User", backref="playlists")
    song_id = db.Column(db.Integer, db.ForeignKey("song.song_id"), nullable=True)
    song = db.relationship("Song", backref="playlists")
    tracks = db.Column(db.Integer, nullable=False)

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@login_manager.user_loader
def load_admin(admin_id):
    return Admin.query.get(admin_id)

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])   #! done
def home():
    if request.method == "POST":
        if (request.form.get("Start") == "Start"):
            return redirect(url_for("login", user_type="user"))
        elif request.form.get("App_Admin_Login") == "Admin Login":
            return redirect(url_for("admin"))
    return render_template("index.html")

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/admin/LogIn", methods=["GET", "POST"])  #! done
def admin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        existing = Admin.query.filter_by(email=email).first()
        if existing and existing.password == password:
            login_user(existing)
            return redirect(url_for("admin_home", name=existing.name))
        else:
            return "Invalid"

    return render_template("admin_login.html")

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/admin")  #! done
@login_required
def admin_home():  # ADMIN DASHBOARD
    # Admin home page logic goes here
    name = current_user.name
    albums = Album.query.all()
    songs = Song.query.all()
    artists = Artist.query.all()
    users = User.query.all()
    total_songs = len(songs)
    total_albums = len(albums)
    total_user = len(users)
    total_artist = len(artists)
    total_rating = 0
    for song in songs:
        total_rating += song.rating
    if(total_rating==0):
        avg_rating =0
    else:
        avg_rating = round(total_rating / total_songs,3)
    
    flagged_songs_count = {}
    for artist in artists:
        flagged_songs_count[artist.name] = 0
        for song in artist.songs:
            if not song.flag:
                flagged_songs_count[artist.name] += 1
        
    # Create graph between Songs and their Rating
    song_titles = [song.title for song in songs]
    song_ratings = [song.rating for song in songs]

    plt.figure(figsize=(10, 6))  # Define the figure size
    plt.bar(song_titles, song_ratings)
    plt.xlabel('Song')
    plt.ylabel('Rating')
    plt.title('Songs and their Ratings')

    # Save the graph to the static folder
    graph2 = 'static/song_rating_graph.png'
    
    plt.savefig(graph2)

    # Clear the figure for the next graph
    plt.clf()
    

    plt.figure(figsize=(10, 6))  # Define the figure size
    bar_width=0.3
    bars1 = plt.bar('Users', total_user, width=bar_width, color='b', align='center')
    bars2 = plt.bar('Artists', total_artist, width=bar_width, color='g', align='center')
    bars3 = plt.bar('Albums', total_albums, width=bar_width, color='r', align='center')
    plt.xlabel('Categories')
    plt.ylabel('Number')
    plt.title('Number of Users, Artists and Albums ')
    plt.legend((bars1[0], bars2[0],bars3[0]), ('Users', 'Artists','Albums'))


    # Save the graph to the static folder
    graph1 = 'static/user_artist_graph.png'
    plt.savefig(graph1)

    # Clear the figure for the next graph
    plt.clf()
    
    
    
            
    return render_template("adminDashboad.html",name=name,artists=artists,total_songs=total_songs,total_albums=total_albums,avg_rating=avg_rating,total_user=total_user,total_artist=total_artist,flagged_songs_count=flagged_songs_count,graph1='../static/user_artist_graph.png',graph2='../static/song_rating_graph.png')

#?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/<x>/flag/<int:id>", methods=["GET","POST"])    #! done
@login_required
def flag(x,id):
    if x=="album":
        album = Album.query.get(id)
        if album:
            if(album.flag):
                album.flag = False
            else:
                album.flag = True
                
            db.session.commit()
            flash("Album flagged successfully", "success")
            return redirect(url_for("adminShowList"))
    if x=="song":
        song = Song.query.get(id)
        if song:
            if(song.flag):
                song.flag = False
            else:
                song.flag = True
                
            db.session.commit()
            flash("Song flagged successfully", "success")
            return redirect(url_for("adminShowList"))
    if x== "artist":
        artist = Artist.query.get(id)
        if artist:
            if(artist.flag):
                artist.flag = False
                for album in artist.albums:
                    album.flag = False
                for song in artist.songs:
                    song.flag = False
                db.session.commit()
                flash("Artist and associated songs/albums flagged successfully", "success")
                return redirect(url_for("admin_home"))
            else:
                artist.flag = True
                for album in artist.albums:
                    album.flag = False
                for song in artist.songs:
                    song.flag = False
                db.session.commit()
                flash("Artist and associated songs/albums flagged successfully", "success")
                return redirect(url_for("admin_home"))
    else:
        return "Invalid object ID"  

#?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/admin/All_tracks_and_albums", methods=["GET", "POST"])  #! done
@login_required
def adminShowList():
    name = current_user.name
    songs = Song.query.all()
    albums = Album.query.all()
    return render_template("All_Tracks_and_Album.html",songs=songs,albums=albums,name=name)

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/SignUp/<user_type>", methods=["GET", "POST"])  #! done
def login(user_type):
    if request.method == "POST":
        optionScreen = request.form.get("optionScreen")
        if optionScreen == "LogIn":
            email = request.form.get("email")
            password = request.form.get("password")
        else:
            name = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")

        # if user_type == "user":
        if optionScreen == "SignUp":
            new_user = User(
                username=name,
                email=email,
                password=password,
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("user_home", user_id=new_user.user_id))
        else:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                if existing_user.password == password:
                    return redirect(url_for("user_home", user_id=existing_user.user_id))
                else:
                    return ("""<body style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                                <div style="text-align: center;">
                                    <h1>Wrong Password</h1>
                                    <h2>Please Enter Correct Password</h2>
                                </div>
                        </body>""")
            else:
                return ("""<body style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                                <div style="text-align: center;">
                                    <h1>Please SignUp</h1>
                                    <h2>User Don't Exist</h2>
                                </div>
                        </body>""")

    return render_template("login.html", action=url_for("login", user_type=user_type))

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/user/<int:user_id>", methods=["GET", "POST"])    #! done
def user_home(user_id):
    genres = Genre.query.all()
    albums = Album.query.all()
    songs = Song.query.all()
    existing_artist = Artist.query.filter_by(user_id=user_id).first()
    if request.method == "POST":
        search = request.form.get("search")
        if search is not None:
            song = Song.query.filter(Song.title.ilike(f'%{search}%')).first()
            album = Album.query.filter(Album.title.ilike(f'%{search}%')).first()
            genre = Genre.query.filter(Genre.name.ilike(f'%{search}%')).first()
            if album:
                return render_template("userhome.html", search=True,album=album, songs=songs, genres=genres, albums=albums, user_id=user_id)
            elif song:
                return render_template("userhome.html", search=True,song=song, songs=songs, genres=genres, albums=albums, user_id=user_id)
            elif genre:
                return render_template("userhome.html", search=True,genre=genre, songs=songs, genres=genres, albums=albums, user_id=user_id)
                
        songs = Song.query.all()
        existing_user = User.query.filter_by(user_id=user_id).first()
        return redirect(url_for("user_home", user_id=existing_user.user_id))

    playlists = Playlist.query.filter_by(user_id=user_id).all()
    l = list()
    preName= ""
    for i in playlists:
        if(i.name != preName):
            l.append(i)
            preName = i.name
                
    if existing_artist:
        return render_template("userhome.html", search=False, songs=songs, genres=genres, albums=albums, user_id=user_id, artist_id=existing_artist.artist_id, playlists=l)
    return render_template("userhome.html", search=False, songs=songs, genres=genres, albums=albums, user_id=user_id, playlists=l)

#?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/playlist/<int:user_id>", methods=["GET", "POST"])    #! done
def playlist(user_id):
    if request.method == "POST":
        selected_songs = request.form.getlist('selected_songs')
        status = request.form.get("status")
        playlistTitle = request.form.get("playlistTitle")
        
        for i in selected_songs:
            playlist = Playlist(name=playlistTitle, status=status,user_id = user_id,song_id = i, tracks =len(selected_songs))
            db.session.add(playlist)
        db.session.commit()
        return redirect(url_for("user_home", user_id=user_id))    
        
    songs = Song.query.all()
    return render_template("playlist.html",songs = songs,user_id=user_id) 

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/edit_playlist/<int:playlist_id>/<Name>", methods=["GET", "POST"])
def edit_playlist(playlist_id, Name):
    playlists = Playlist.query.filter_by(name=Name).all()
    if request.method == "POST":
        status = request.form.get("status")
        name = request.form.get("name")
        for playlist in playlists:
            playlist.name = name
            playlist.status = status
        db.session.commit()
        flash("Playlists updated successfully", "success")
        return redirect(url_for("showList", x="playlist", user_id=playlists[0].user_id, id=playlist_id, Name=name))
    return render_template("edit_playlist.html", playlists=playlists, playlist_id=playlist_id,name = Name)

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/<x>/showId/<int:user_id>/<int:id>/<Name>", methods=["GET", "POST"])   #! done
def showList(x, user_id, id, Name):
    # Check if the ID belongs to a playlist
    existing_artist = Artist.query.filter_by(user_id=user_id).first()
    
    if x == "playlist":
        # Query playlists with the specified name and user ID
        playlists = Playlist.query.filter_by(name=Name, user_id=user_id).all()
        
        delete = request.form.get("Delete")
        if delete:
            s_id = int(delete[6:])
            temp = Playlist.query.filter_by(song_id=s_id).first()
            if temp:
                temp.song_id = None
                db.session.commit()

        if playlists:
            # Fetch the playlist data from the database
            name = playlists[0].name  # Get the name from the first playlist (assuming unique names)
            song_ids = [playlist.song_id for playlist in playlists]
            songs = Song.query.filter(Song.song_id.in_(song_ids)).all()

            if existing_artist:
                return render_template("showlist.html", songs=songs, name=name, playlist_id=id, user_id=user_id, artist_id=existing_artist.artist_id, plist=True, status=False)

            return render_template("showlist.html", songs=songs, name=name, playlist_id=id, user_id=user_id, plist=True, status=False)

    if x == "album":
        # Check if the ID belongs to an album
        album = Album.query.get(id)
        if album:
            # Fetch the album data from the database
            name= album.title
            songs = Song.query.filter_by(album_id=id).all()
            if existing_artist:
                return render_template("showlist.html", songs=songs, name=name,user_id=user_id,artist_id=existing_artist.artist_id,album=True, status=True)
            return render_template("showlist.html", songs=songs, name=name,user_id=user_id,album=True, status=True)
        
    if x== "genre":
        # # Check if the ID belongs to a genre
        genre = Genre.query.get(id)
        if genre:
            # Fetch the genre data from the database
            name= genre.name
            songs = Song.query.filter_by(genre_id=id).all()
            if existing_artist:
                return render_template("showlist.html", songs=songs, name=name,user_id=user_id,artist_id=existing_artist.artist_id,genre=True, status=True)
            return render_template("showlist.html", songs=songs, name=name,user_id=user_id,genre=True, status=True)

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/artist/<int:user_id>", methods=["GET", "POST"])    #! done
def artist(user_id):
    if request.method == "POST":
        existing_user = User.query.filter_by(user_id=user_id).first()
        artist_name = existing_user.username

        # Check if an artist with the same name exists
        existing_artist = Artist.query.filter_by(name=artist_name).first()

        if existing_artist:
            if existing_artist.flag:
                return redirect(url_for("artist_home", artist_id=existing_artist.artist_id))
            else:
                return ("""<body style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                                <div style="text-align: center;">
                                    <h1>You Are Blacklisted</h1>
                                </div>
                        </body>""")
                
        
        new_artist = Artist(name=artist_name,user_id=user_id)
        db.session.add(new_artist)
        db.session.commit()
        
        return redirect(url_for("artist_home", artist_id=new_artist.artist_id))
    
    return render_template("artist.html", user_id=user_id)

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/artist_home/<int:artist_id>")  #! done
def artist_home(artist_id):
    artist = Artist.query.filter_by(artist_id=artist_id).first()
    
    if artist:
            if artist.flag:
                return render_template("artistAcc.html", artist_id=artist.artist_id,user_id=artist.user_id)
            else:
                return ("""<body style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                                <div style="text-align: center;">
                                    <h1>You Are Blacklisted</h1>
                                </div>
                        </body>""")
    else:
        return ("""<body style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                                <div style="text-align: center;">
                                    <h1>You Are Not Artist</h1>
                                </div>
                        </body>""")


# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/artist_dashboad/<int:artist_id>")          #! done
def artist_dashboad(artist_id):
    artist = Artist.query.filter_by(artist_id=artist_id).first()
    songs = Song.query.filter_by(artist_id=artist_id).all()
    albums = Album.query.filter_by(artist_id=artist_id).all()
    total_songs = len(songs)
    total_rating = 0
    for song in songs:
        total_rating += song.rating
    if(total_rating==0):
        avg_rating =0
    else:
        avg_rating = round(total_rating / total_songs,3)
    total_albums = Album.query.filter_by(artist_id=artist_id).count()
    song_titles = [song.title for song in songs]
    song_ratings = [song.rating for song in songs]

    plt.figure(figsize=(10, 6))  # Define the figure size
    plt.bar(song_titles, song_ratings)
    plt.xlabel('Song')
    plt.ylabel('Rating')
    plt.title('Songs and their Ratings')

    # Save the graph to the static folder
    graph = 'static/Artist_song_rating_graph.png'
    
    plt.savefig(graph)

    # Clear the figure for the next graph
    plt.clf()
    if artist:
            if artist.flag:
                return render_template("artistDashboad.html", songs=songs,albums=albums, artist=artist, total_songs=total_songs, total_albums=total_albums, avg_rating=avg_rating, artist_id=artist_id,graph="../static/Artist_song_rating_graph.png")
            else:
                return ("""<body style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                                <div style="text-align: center;">
                                    <h1>You Are Blacklisted</h1>
                                </div>
                        </body>""")
    else:
        return ("""<body style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                                <div style="text-align: center;">
                                    <h1>You Are Not Artist</h1>
                                </div>
                        </body>""")

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/edit_album/<int:album_id>", methods=["GET", "POST"])          #! done
def edit_album(album_id):
    album = Album.query.get(album_id)
    if request.method == "POST":
        album.title = request.form.get("title")
        album.release = request.form.get("release")
        album.duration = float(request.form.get("duration"))
        db.session.commit()
        flash("Album updated successfully", "success")
        return redirect(url_for("artist_dashboad", artist_id=album.artist_id))
    return render_template("editAlbum.html", album=album)

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/edit_song/<int:song_id>", methods=["GET", "POST"])          #! done
def edit_song(song_id):
    song = Song.query.get(song_id)
    album = Album.query.get(song.album_id)
    genre = Genre.query.get(song.genre_id)  # Get the genre object associated with the song
    if request.method == "POST":
        # Handle the form submission here
        title = request.form.get("title")
        singer = request.form.get("singer")
        date = request.form.get("date")
        duration = float(request.form.get("time"))
        lyrics = request.form.get("lyrics")
        album_title = request.form.get("albumTitle")
        genre_name = request.form.get("genreName")

        # Check if the selected genre and album exist, if not, add them
        genre = Genre.query.filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.session.add(genre)

        album = Album.query.filter_by(title=album_title).first()
        if not album:
            album = Album(title=album_title, release=date, duration=duration, artist_id=song.artist_id)
            db.session.add(album)
            db.session.commit()  # Commit the album to generate the album_id

        # Update the song details
        song.title = title
        song.lyrics = lyrics
        song.artistname = singer
        song.release = date
        song.duration = duration
        song.genre_id = genre.genre_id
        song.album_id = album.album_id

        db.session.commit()

        flash("Song updated successfully", "success")
        return redirect(url_for("artist_dashboad", artist_id=song.artist_id))

    return render_template("edit_song.html", song=song, album=album, genre=genre)

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/delete_song/<int:song_id>", methods=["GET", "POST"])          #! done
def delete_song(song_id):
    song = Song.query.get(song_id)
    
    if song:
        artist_id = song.artist_id

        # Find and update the playlists containing the song
        playlists = Playlist.query.filter(Playlist.song_id == song_id).all()
        
        for playlist in playlists:
            if playlist.song_id == song_id:
                # Remove the song from the playlist
                playlist.song_id = None
                playlist.tracks -= 1
        
        # Delete the song from the database
        db.session.delete(song)
        db.session.commit()
        
        # Delete the song file from the local device
        audio_path = os.path.join(app.config["UPLOAD_FOLDER"], song.mp3_path.split("/")[-1])
        image_path = os.path.join(app.config["IMAGE_FOLDER"], song.image_path.split("/")[-1])
        
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(image_path):
            os.remove(image_path)
        
        # Delete the song from all related tables
        album = Album.query.filter_by(album_id=song.album_id).first()
        if album:
            tDuration = album.duration - song.duration  # Update the total duration of the existing album
            album.duration = tDuration
            db.session.commit()
        Song.query.filter(Song.song_id == song_id).delete()
        Playlist.query.filter(Playlist.song_id == song_id).delete()
        
        flash("Song deleted successfully", "success")
        return redirect(url_for("artist_dashboad", artist_id=artist_id))
    else:
        flash("Song not found", "error")
    
# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/delete_playlist/<int:user_id>/<name>", methods=["GET", "POST"])
def delete_playlist(user_id, name):
    playlists = Playlist.query.filter_by(user_id=user_id, name=name).all()
        
    if playlists:
        # Delete the playlists from the database
        for playlist in playlists:
            db.session.delete(playlist)
        db.session.commit()
        
        flash("Playlists deleted successfully", "success")
        return redirect(url_for("user_home", user_id=user_id))
    else:
        flash("Playlists not found", "error")
        return redirect(url_for("user_home", user_id=user_id))


# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/delete_album/<int:album_id>", methods=["GET", "POST"])          #! done
def delete_album(album_id):
    album = Album.query.get(album_id)
    
    if album:
        artist_id = album.artist_id
        
        # Delete the album from the database
        db.session.delete(album)
        db.session.commit()
        
        # Delete all songs associated with the album
        songs = Song.query.filter_by(album_id=album_id).all()
        for song in songs:
            db.session.delete(song)
        
        flash("Album deleted successfully", "success")
        return redirect(url_for("artist_dashboad", artist_id=artist_id))
    else:
        flash("Album not found", "error")

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/upload/<int:artist_id>", methods=["GET", "POST"])          #! done
def upload(artist_id):

    if request.method == "POST":
        # Handle the form submission here
        audio_file = request.files["audio_file"]
        image_file = request.files["image_file"]
        title = request.form.get("title")
        singer = request.form.get("singer")
        date = request.form.get("date")
        duration = float(request.form.get("time"))
        lyrics = request.form.get("lyrics")
        album_title = request.form.get("albumTitle")
        genre_name = request.form.get("genreName")

        # Check if the selected genre and album exist, if not, add them
        genre = Genre.query.filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.session.add(genre)

        album = Album.query.filter_by(title=album_title).first()
        if not album:
            tDuration = duration  # Initialize total duration to the current song's duration
            album = Album(title=album_title, release=date, duration=tDuration, artist_id=artist_id)
            db.session.add(album)
            db.session.commit()
        else:
            tDuration = album.duration + duration  # Update the total duration of the existing album
            album.duration = tDuration
            db.session.commit()

        # Continue with the song upload
        if audio_file and image_file:
            audio_path = os.path.join(app.config["UPLOAD_FOLDER"], audio_file.filename)
            image_path = os.path.join(app.config["IMAGE_FOLDER"], image_file.filename)

            audio_file.save(audio_path)
            image_file.save(image_path)

            new_song = Song(
                title=title,
                lyrics=lyrics,
                image_path='/images/' + image_file.filename,
                mp3_path='/audio/' + audio_file.filename,
                artist_id=artist_id,
                artistname=singer,
                release=date,
                duration=duration,
                genre_id=genre.genre_id,
                album_id=album.album_id  # Set the album_id
            )
            db.session.add(new_song)
            db.session.commit()

        return redirect(url_for("artist_dashboad", artist_id=artist_id))  # Corrected endpoint name

    return render_template('upload.html', artist_id=artist_id)

# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/play/<int:song_id>',methods=["GET", "POST"])     #! done
def play(song_id):
    song = Song.query.get(song_id)
    if song:
        if request.method == "POST":
            rating = int(request.form.get("rating"))
            song.rating = rating
            db.session.commit()
            flash("Rating updated successfully", "success")
        return render_template('play.html', song=song)
    else:
        return "Song not found", 404
# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/logout")
@login_required 
def log_user_out():
    logout_user()
    return redirect('/')
# ?---------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
