#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import collections
from markupsafe import Markup
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
collections.Callable = collections.abc.Callable

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

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
    num_upcoming_shows = db.Column(db.Integer)
    num_past_shows = db.Column(db.Integer)
    genres = db.Column(db.String(500))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.String(20)) 
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy='dynamic')


    def __repr__(self):
      return f'<Venue {self.id}, {self.name}, {self.city}, {self.state}, {self.address}, {self.phone}, {self.image_link}, {self.facebook_link}, {self.num_upcoming_shows}, {self.num_past_shows}, {self.genres}, {self.website}, {self.seeking_talent}, {self.seeking_description}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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
    upcoming_shows_count = db.Column(db.Integer)
    past_shows_count = db.Column(db.Integer)
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.String(10)) 
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy='dynamic')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
def __repr__(self):
      return f'<Venue {self.id}, {self.name}, {self.city}, {self.state}, {self.phone}, {self.genres}, {self.image_link}, {self.facebook_link}, {self.upcoming_shows_count}, {self.past_shows_count}, {self.website}, {self.seeking_venue}, {self.seeking_description}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __table__name = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  start_time = db.Column(db.DateTime(timezone=True))
  upcoming_shows = db.Column(db.DateTime(timezone=True))

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venue = Venue.query.order_by('id').all()
  data = []
  for v in venue:
    data += [{
      "city":v.city,
      "state":v.state,
      "venues":[{
        "id":v.id,
        "name":v.name,
        "num_upcoming_shows":v.num_upcoming_shows
      }]
    }]
  return render_template('pages/venues.html', areas=data);

  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '') #getting the search term from form

  search_word = format(search_term.lower()) #Ensure it is case-insensitive.

  results ={}
  results = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_word)) | Venue.city.ilike('%{}%'.format(search_word)) | Venue.state.ilike('%{}%'.format(search_word))).all()

  response = {'count':len(results),'data':results}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue_data = Venue.query.filter_by(id=venue_id).first()

  upcoming_show_query = db.session.query(Show.start_time, Artist.id, Artist.name, Artist.image_link).join(Venue, Artist).filter(Show.start_time > datetime.today(),Show.venue_id==venue_data.id).all()
  
  past_show_query = db.session.query(Show.start_time, Artist.id, Artist.name, Artist.image_link).join(Venue, Artist).filter(Show.start_time < datetime.today(),Show.venue_id==venue_data.id).all()
 
  upcoming_shows = []
  for start_time, artist_id, artist_name, image_link in upcoming_show_query:
    upcoming_shows.append(
      {
        "artist_id": artist_id,
        "artist_name": artist_name,
        "artist_image_link": image_link,
        "start_time": format_datetime(str(start_time))
      }
    )

  past_shows = []
  for start_time, artist_id, artist_name, image_link in past_show_query:
    past_shows.append(
      {
        "artist_id": artist_id,
        "artist_name": artist_name,
        "artist_image_link": image_link,
        "start_time": format_datetime(str(start_time))
      }
    )
  
  data={
    "id":venue_data.id,
    "name":venue_data.name,
    "genres": venue_data.genres.split(","),
    "address":venue_data.address,
    "city":venue_data.city,
    "state":venue_data.state,
    "phone":venue_data.phone,
    "website":venue_data.website,
    "facebook_link":venue_data.facebook_link,
    "seeking_talent":venue_data.seeking_talent,
    "seeking_description": venue_data.seeking_description,
    "image_link":venue_data.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_show_query),
    "upcoming_shows_count": len(upcoming_show_query),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm(request.form)
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
# on successful db insert, flash success
  if form.validate():
    try:
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      phone = request.form.get('phone')
      address = request.form.get('address')
      genres = request.form.get('genres')
      facebook_link = request.form.get('facebook_link')
      image_link = request.form.get('image_link')
      website_link = request.form.get('website_link')
      seeking_talent = request.form.get('seeking_talent')
      seeking_description = request.form.get('seeking_description')

      data = Venue(name=name, city=city, state=state, phone=phone, address=address, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website_link, seeking_talent= seeking_talent, seeking_description=seeking_description)
      db.session.add(data)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

      
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    finally:
      db.session.close()
  else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'ERR.')
# TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    v_delete = Venue.query.get(venue_id)
    db.session.delete(v_delete)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')

  search_word = format(search_term.lower())

  results ={}
  results = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_word)) | Artist.city.ilike('%{}%'.format(search_word)) | Artist.state.ilike('%{}%'.format(search_word))).all()

  response = {'count':len(results),
              'data':results}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist_data = Artist.query.filter_by(id=artist_id).first()
  upcoming_show_query = db.session.query(Show.start_time, Venue.id, Venue.name, Venue.image_link).join(Venue, Artist).filter(Show.start_time>=datetime.today(),Show.artist_id==artist_data.id).all()
  past_show_query = db.session.query(Show.start_time, Venue.id, Venue.name, Venue.image_link).join(Venue, Artist).filter(Show.start_time<datetime.today(),Show.artist_id==artist_data.id).all()
  
  upcoming_shows = []
  for start_time, venue_id, venue_name, image_link in upcoming_show_query:
    upcoming_shows.append(
      {
        "venue_id": venue_id,
        "venue_name": venue_name,
        "venue_image_link": image_link,
        "start_time": format_datetime(str(start_time))
      }
    )

  past_shows = []
  for start_time, venue_id, venue_name, image_link in past_show_query:
    past_shows.append(
      {
        "venue_id": venue_id,
        "venue_name": venue_name,
        "venue_image_link": image_link,
        "start_time": format_datetime(str(start_time))
      }
    )

  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  data={
    "id": artist_id,
    "name":artist_data.name,
    "genres":artist_data.genres.split(","),
    "city":artist_data.city,
    "state":artist_data.state,
    "phone":artist_data.phone,
    "website":artist_data.website,
    "facebook_link":artist_data.facebook_link,
    "seeking_venue":artist_data.seeking_venue,
    "seeking_description":artist_data.seeking_description,
    "image_link":artist_data.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_show_query),
    "upcoming_shows_count": len(upcoming_show_query),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  data = Artist.query.get(artist_id)
  try:

    data.name = request.form.get('name')
    data.city = request.form.get('city')
    data.state = request.form.get('state')
    data.phone = request.form.get('phone')
    data.genres = request.form.get('genres')
    data.image_link = request.form.get('image_link')
    data.facebook_link = request.form.get('facebook_link')
    data.website = request.form.get('website_link')
    data.seeking_venue = request.form.get('seeking_venue')
    data.seeking_description = request.form.get('seeking_description')
    
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  data = Venue.query.get(venue_id)
  try:
    data.name = request.form.get('name')
    data.city =  request.form.get('city')
    data.state = request.form.get('state')
    data.phone = request.form.get('phone')
    data.address = request.form.get('address')
    data.genres = request.form.get('genres')
    data.image_link =  request.form.get('image_link')
    data.facebook_link = request.form.get('facebook_link')
    data.website = request.form.get('website_link')
    data.seeking_venue = request.form.get('seeking_venue')
    data.seeking_description = request.form.get('seeking_description')

    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  if form.validate():
    try:
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      phone = request.form.get('phone')
      genres = ",".join(request.form.get('genres'))
      facebook_link = request.form.get('facebook_link')
      image_link = request.form.get('image_link')
      website_link = request.form.get('website_link')
      seeking_venue = request.form.get('seeking_venue')
      seeking_description = request.form.get('seeking_description')
      

      data = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website_link, seeking_venue = seeking_venue, seeking_description=seeking_description)
      db.session.add(data)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
      for field, message in form.errors.items():
          flash(field + ' - ' + str(message), 'ERR.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data =[]
  shows =  Show.query.all()
  for show in shows:
      artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
      venue = db.session.query(Venue.name).filter(Venue.id == show.venue_id).one()
      data.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": show.artist_id,
        "artist_name":artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.strftime('%m/%d/%Y')
      })
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
#   form = ShowForm()
#   try:
#     show = Show(
#       artist_id = form.artist_id.data,
#       venue_id = form.venue_id.data,
#       start_time=form.start_time.data,
#     )
#     db.session.add(show)
#     db.session.commit()
#   # on successful db insert, flash success
#   flash('Show was successfully listed!')
#   # TODO: on unsuccessful db insert, flash an error instead.
#   # e.g., flash('An error occurred. Show could not be listed.')
#   # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
#   except Exception as e:
#     print(e)
#     flash('An error occurred. Show could not be listed.')
#     db.session.rollback()
#   finally:
#     db.session.close()
#   # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
#   return render_template('pages/home.html')

# def past_shows(shows):
  
#   past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  
#   past_shows = []
  
#   for show in past_shows:
#     if show.start_time < datetime.now():
#       past_shows.append({
#         "venue_id": show.venue_id,
#         "venue_name": show.venue.name,
#         "artist_image_link": show.venue.image_link,
#         "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
#       })
#     return past_shows


# def upcoming_shows(shows):
  
#   upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  
#   upcoming_shows = []
  
#   for show in upcoming_shows:
#     upcoming_shows.append({
#       "venue_id": show.venue_id,
#       "venue_name": show.venue.name,
#       "artist_image_link": show.venue.image_link,
#       "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
#     })
#     return upcoming_shows
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
'''if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
