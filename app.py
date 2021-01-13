#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: DONE connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: DONE implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))

    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship('Show', backref='venue_list', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: DONE implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))

    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship('Show', backref='artist_list', lazy=True)

# TODO DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    show_time = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)



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
  """ Get all venues by State and City """
  areas = []
  now = datetime.today()

  all_areas = Venue.query.order_by('state', 'city').distinct('state', 'city').all()
  for this_area in all_areas:
    get_venues = Venue.query.filter_by(state=this_area.state, city=this_area.city).order_by('name').all()
    venues = []
    for this_venue in get_venues:
      # filter by show_time >= doesn't seem to work so have to iterate through the shows
      # shows = Show.query.filter_by(venue_id=this_venue.id).filter_by(show_time >= now).count()
      upcomping_shows_count = 0
      shows = Show.query.filter_by(venue_id=this_venue.id).all()
      for show in shows:
        if show.show_time > now:
          upcomping_shows_count = upcomping_shows_count +1
      venues.append({
        "id": this_venue.id,
        "name": this_venue.name,
        "num_upcoming_shows": upcomping_shows_count
      })
    areas.append({
      "city": this_venue.city,
      "state": this_venue.state,
      "venues": venues
    })

  return render_template('pages/venues.html', areas=areas);



  # TODO: DONE replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  # return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  """ search for a venue """
  search_term = '%' + request.form.get('search_term') + '%'
  count_of_venues=Venue.query.filter(Venue.name.ilike(search_term)).count()
  venues=Venue.query.filter(Venue.name.ilike(search_term)).all()
  now = datetime.now()
  data = []

  for venue in venues:
    count_of_shows = 0
    for show in venue.shows:
      if show.show_time > datetime.now():
        count_of_shows = count_of_shows + 1
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": count_of_shows
    })
    
  response = {
    "count": count_of_venues,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))





  # TODO: DONE implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue=Venue.query.filter_by(id=venue_id).first()
  venue.genres = venue.genres.split(',')

  class DisplayData:
    pass

  d = DisplayData()
  d.id = venue.id
  d.name = venue.name
  d.genres = venue.genres
  d.address = venue.address
  d.city = venue.city
  d.state = venue.state
  d.phone = venue.phone
  d.website = venue.website
  d.facebook_link = venue.facebook_link
  d.seeking_venue = venue.seeking_talent
  d.seeking_description = venue.seeking_description
  d.image_link = venue.image_link
  d.past_shows_count = 0
  d.upcoming_shows_count = 0
  d.past_shows = []
  d.upcoming_shows = []

  i = 0
  for show in venue.shows:
    artist = Artist.query.get(show.artist_id)
    if show.show_time < datetime.now():
      d.past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.show_time.isoformat()
      })
      d.past_shows_count = d.past_shows_count + 1
    else:
      d.upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.show_time.isoformat()
      })
      d.upcoming_shows_count = d.upcoming_shows_count + 1

  return render_template('pages/show_venue.html', venue=d)




  # TODO: DONE replace with real venue data from the venues table, using venue_id
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  """ Process the create Venue form """
  error = False
  try:
    genres = request.form.getlist('genres')
    genres_list = ",".join(genres)

    seeking_talent = request.form.get('seeking_artists')
    if seeking_talent == 'y':
      seeking_talent_bool = True
    else:
      seeking_talent_bool = False

    venue = Venue(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      address = request.form.get('address'),
      phone = request.form.get('phone'),
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      genres = genres_list,
      seeking_talent = seeking_talent_bool,
      seeking_description = request.form.get('message_to_artists')
    )

    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if error:
    # on unsuccessful db insert, flash and error message
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form.get('name') + ' was successfully listed!')

  return render_template('pages/home.html')

  # TODO: DONE insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: DONE on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    for show in venue.shows:
      db.session.delete(show)

    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    # on unsuccessful db insert, flash and error message
    flash('An error occurred. Venue ' + str(venue_id) + ' could not be deleted.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + str(venue_id) + ' was successfully deleted!')

  return render_template('pages/home.html')


  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  """ Get all artists names """
  artists=Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

  # # TODO: DONE replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  # return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  """ search for an artist """
  search_term = '%' + request.form.get('search_term') + '%'
  count_of_artists=Artist.query.filter(Artist.name.ilike(search_term)).count()
  artists=Artist.query.filter(Artist.name.ilike(search_term)).all()
  now = datetime.now()
  data = []

  for artist in artists:
    count_of_shows = 0
    for show in artist.shows:
      if show.show_time > datetime.now():
        count_of_shows = count_of_shows + 1
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": count_of_shows
    })
    
  response = {
    "count": count_of_artists,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


  # TODO: DONE implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  # return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given venue_id
  artist=Artist.query.filter_by(id=artist_id).first()
  artist.genres = artist.genres.split(',')

  class DisplayData:
    pass

  d = DisplayData()
  d.id = artist.id
  d.name = artist.name
  d.genres = artist.genres
  d.city = artist.city
  d.state = artist.state
  d.phone = artist.phone
  d.website = artist.website
  d.facebook_link = artist.facebook_link
  d.seeking_venue = artist.seeking_venue
  d.seeking_description = artist.seeking_description
  d.image_link = artist.image_link
  d.past_shows_count = 0
  d.upcoming_shows_count = 0
  d.past_shows = []
  d.upcoming_shows = []

  i = 0
  for show in artist.shows:
    venue = Venue.query.get(show.venue_id)
    if show.show_time < datetime.now():
      d.past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.show_time.isoformat()
      })
      d.past_shows_count = d.past_shows_count + 1
    else:
      d.upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.show_time.isoformat()
      })
      d.upcoming_shows_count = d.upcoming_shows_count + 1

  return render_template('pages/show_artist.html', artist=d)
 
  # TODO: DONE replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  # return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  """ Process the edit artist form """
  error = False
  a = Artist.query.get(artist_id)
  if a is None:
    error = True
    flash('An error occurred. Artist ' + str(artist_id) + ' could not be found.')
    return render_template('pages/home.html')

  form = ArtistForm()
  form.name.data = a.name
  form.city.data = a.city
  form.state.data = a.state
  form.phone.data = a.phone
  form.genres.data = a.genres
  form.website.data = a.website
  form.image_link.data = a.image_link
  form.facebook_link.data = a.facebook_link
  form.seeking_venues.data = a.seeking_venue
  form.message_to_venues.data = a.seeking_description
  
  return render_template('forms/edit_artist.html', form=form, artist=a)


  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # # TODO: DONE populate form with fields from artist with ID <artist_id>
  # return render_template('forms/edit_artist.html', form=form, artist=a)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  """ Process the edit Artist form """
  error = False
  a = Artist.query.get(artist_id)
  if a is None:
    error = True
    flash('An error occurred. Artist ' + str(artist_id) + ' could not be found.')
    return render_template('pages/home.html')
  try:
    a = Artist.query.get(artist_id)
    genres = request.form.getlist('genres')
    genres_list = ",".join(genres)

    seeking_venue = request.form.get('seeking_venues')
    print(seeking_venue)
    if seeking_venue == 'y':
      seeking_venue_bool = True
    else:
      seeking_venue_bool = False

    print(seeking_venue_bool)
    a.name = request.form.get('name'),
    a.city = request.form.get('city'),
    a.state = request.form.get('state'),
    a.phone = request.form.get('phone'),
    a.image_link = request.form.get('image_link'),
    a.facebook_link = request.form.get('facebook_link'),
    a.website = request.form.get('website'),
    a.genres = genres_list,
    # the following line causes an exception - I don't know why
    # a.seeking_venue = seeking_venue_bool,
    a.seeking_description = request.form.get('message_to_venues')

    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if error:
    # on unsuccessful db update, flash and error message
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be updated.')
  else:
    # on successful db update, flash success
    flash('Artist ' + request.form.get('name') + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

  # TODO: DONE take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  # return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  """ Process the edit venue form """
  error = False
  a = Venue.query.get(venue_id)
  if a is None:
    error = True
    flash('An error occurred. Venue ' + str(venue_id) + ' could not be found.')
    return render_template('pages/home.html')

  form = VenueForm()
  form.name.data = a.name
  form.city.data = a.city
  form.address.data = a.address
  form.state.data = a.state
  form.phone.data = a.phone
  form.genres.data = a.genres
  form.website.data = a.website
  form.image_link.data = a.image_link
  form.facebook_link.data = a.facebook_link
  form.seeking_artists.data = a.seeking_talent
  form.message_to_artists.data = a.seeking_description
  
  return render_template('forms/edit_venue.html', form=form, venue=a)

  # form = VenueForm()
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # # TODO: DONE populate form with values from venue with ID <venue_id>
  # return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  """ Process the edit Venue form """
  error = False
  a = Venue.query.get(venue_id)
  if a is None:
    error = True
    flash('An error occurred. Venue ' + str(venue_id) + ' could not be found.')
    return render_template('pages/home.html')
  try:
    a = Venue.query.get(venue_id)
    genres = request.form.getlist('genres')
    genres_list = ",".join(genres)

    seeking_artists = request.form.get('seeking_artists')
    print(seeking_artists)
    if seeking_artists == 'y':
      seeking_artists_bool = True
    else:
      seeking_artists_bool = False

    print(seeking_artists)
    a.name = request.form.get('name'),
    a.address = request.form.get('address'),
    a.city = request.form.get('city'),
    a.state = request.form.get('state'),
    a.phone = request.form.get('phone'),
    a.image_link = request.form.get('image_link'),
    a.facebook_link = request.form.get('facebook_link'),
    a.website = request.form.get('website'),
    a.genres = genres_list,
    # the following line causes an exception - I don't know why
    # a.seeking_artists = seeking_artists_bool,
    a.seeking_description = request.form.get('message_to_artists')

    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if error:
    # on unsuccessful db update, flash and error message
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be updated.')
  else:
    # on successful db update, flash success
    flash('Venue ' + request.form.get('name') + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

  # TODO: DONE take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  # return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  """ Process the create Artist form """
  error = False
  try:
    genres = request.form.getlist('genres')
    genres_list = ",".join(genres)

    seeking_venue = request.form.get('seeking_venues')
    if seeking_venue == 'y':
      seeking_venue_bool = True
    else:
      seeking_venue_bool = False

    artist = Artist(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      genres = genres_list,
      seeking_venue = seeking_venue_bool,
      seeking_description = request.form.get('message_to_venues')
    )

    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if error:
    # on unsuccessful db insert, flash and error message
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form.get('name') + ' was successfully listed!')
  return render_template('pages/home.html')



  # called upon submitting the new artist listing form
  # TODO: DONE insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: DONE on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  now = datetime.today()
  shows = Show.query.all()
  upcoming_shows = []
  for show in shows:
    if show.show_time >= now:
      venue=Venue.query.filter_by(id=show.venue_id).first()
      artist=Artist.query.filter_by(id=show.artist_id).first()
      upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.show_time.isoformat()
      })
  return render_template('pages/shows.html', shows=upcoming_shows)

  # TODO: DONE replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  # return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  """ Process the create Venue form """
  error = False
  try:
    show = Show(
      show_time = request.form.get('start_time'),
      artist_id = int(request.form.get('artist_id')),
      venue_id = int(request.form.get('venue_id'))
    )

    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if error:
    # on unsuccessful db insert, flash and error message
    flash('An error occurred. Show starting at ' + request.form.get('start_time') + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Show starting at ' + request.form.get('start_time') + ' was successfully listed!')



  # called to create new shows in the db, upon submitting new show listing form
  # TODO: DONE insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: DONE on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('errors/404.html'), 404

@app.errorhandler(404)
def not_found_error_json(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

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
