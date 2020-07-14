#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

shows = db.Table('shows',
                db.Column('id', db.Integer, primary_key=True),
                db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), nullable=False),
                db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), nullable=False),
                db.Column('start_time', db.DateTime, nullable=False),
                db.UniqueConstraint('artist_id', 'venue_id', 'start_time'),
                db.UniqueConstraint('artist_id', 'start_time')
                # didn't add venue with start_time to unique constraint as a venue could have multiple halls , 
                # so more than artist/band performing at the same time at the same venue
                )

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    venues = db.relationship('Venues', secondary=shows, backref='artists')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

def getList(genres):
  return genres.replace('{','').replace('}','').split(',')


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = Venue.query.order_by(Venue.state).order_by(Venue.city).all()
  data = []
  if (len(venues)>0):
    data.append({'city':venues[0].city,'state':venues[0].state,'venues':[]})
  for venue in venues:
    num_upcoming_shows = 0
    for show in venue.shows:
      if show.start_time>datetime.today():
        num_upcoming_shows+=1
    curVenue={'id':venue.id,'name':venue.name,'num_upcoming_shows':num_upcoming_shows}
    if venue.state!=data[-1].get('state') and venue.city!=data[-1].get('city'):
      data.append({'city':venue.city,'state':venue.state,'venues':[]})
    data[-1].get('venues').append(curVenue)
    
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  
  response = {}
  response['count']=len(venues)
  response['data']=[]
  for venue in venues:
    curVenue={}
    curVenue['id']=venue.id
    curVenue['name']=venue.name
    num_upcoming_shows=0
    for show in venue.shows:
      if (show.start_time>datetime.today()):
        num_upcoming_shows+=1
    curVenue['num_upcoming_shows']=num_upcoming_shows
    response['data'].append(curVenue)
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)

  data = {}

  data['id']=venue.id
  data['name']=venue.name
  data['genres']=getList(venue.genres)
  data['address']=venue.address
  data['city']=venue.city
  data['state']=venue.state
  data['phone']=venue.phone
  data['facebook_link']=venue.facebook_link
  data['image_link']=venue.image_link

  past_shows=[]
  upcoming_shows=[]
  for show in venue.shows :
    curShow={}
    curShow['artist_id']=show.artist.id
    curShow['artist_name']=show.artist.name
    curShow['artist_image_link']=show.artist.image_link
    curShow['start_time']=str(show.start_time)
    if (show.start_time<datetime.today()):
      past_shows.append(curShow)
    else :
      upcoming_shows.append(curShow)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  data={}
  try:
    name = request.form.get('name','')
    genres = request.form.getlist('genres')
    city = request.form.get('city','')
    state = request.form.get('state','')
    address = request.form.get('address','')
    phone = request.form.get('phone','')
    facebook_link = request.form.get('facebook_link','')
    image_link = request.form.get('image_link','')

    venue = Venue(name=name,genres=genres,city=city,state=state,address=address,phone=phone,facebook_link=facebook_link,image_link=image_link)
    data['name'] = venue.name
    db.session.add(venue)

    db.session.commit()
    flash('Venue ' + data['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
  finally:
    db.session.close()
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  
  response = {}
  response['count']=len(artists)
  response['data']=[]
  for artist in artists:
    curArtist={}
    curArtist['id']=artist.id
    curArtist['name']=artist.name
    num_upcoming_shows=0
    for show in artist.shows:
      if (show.start_time>datetime.today()):
        num_upcoming_shows+=1
    curArtist['num_upcoming_shows']=num_upcoming_shows
    response['data'].append(curArtist)
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  data={}
  data['id'] = artist.id
  data['name'] = artist.name
  data['genres'] = getList(artist.genres)
  data['state'] = artist.state
  data['phone'] = artist.phone
  data['facebook_link'] = artist.facebook_link
  
  past_shows=[]
  upcoming_shows=[]
  for show in artist.shows :
    curShow={}
    curShow['venue_id']=show.venue.id
    curShow['venue_name']=show.venue.name
    curShow['venue_image_link']=show.venue.image_link
    curShow['start_time']=str(show.start_time)
    if (show.start_time<datetime.today()):
      past_shows.append(curShow)
    else :
      upcoming_shows.append(curShow)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.state.default = artist.state
  form.genres.default = getList(artist.genres)
  form.process()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.state.default = venue.state
  form.genres.default = getList(venue.genres)
  form.process()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  data={}
  try:
    name = request.form.get('name','')
    genres = request.form.getlist('genres')
    city = request.form.get('city','')
    state = request.form.get('state','')
    phone = request.form.get('phone','')
    facebook_link = request.form.get('facebook_link','')
    image_link = request.form.get('image_link','')

    artist = Artist(name=name,genres=genres,city=city,state=state,phone=phone,facebook_link=facebook_link,image_link=image_link)
    data['name'] = artist.name
    db.session.add(artist)

    db.session.commit()
    flash('Artist ' + data['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
  finally:
    db.session.close()

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    curShow = {}
    curShow['venue_id'] = show.venue.id
    curShow['venue_name'] = show.venue.name
    curShow['artist_id'] = show.artist.id
    curShow['artist_name'] = show.artist.name
    curShow['artist_image_link'] = show.artist.image_link
    curShow['start_time'] = str(show.start_time)
    data.append(curShow)
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    artist_id = request.form.get('artist_id', 1)
    venue_id = request.form.get('venue_id', 1)
    start_time = request.form.get('start_time', datetime.today())

    show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
  
    db.session.add(show)

    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
