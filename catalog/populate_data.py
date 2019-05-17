#!/usr/bin/env python3

'''
    File name: populate_data.py
    Author: Khalid Saleem
    Date created: 08/03/2019
    Date last modified: 28/03/2019
    Description: to populate sample data in sqlite database for a web
    application that provides a list of items within a variety of categories
    and integrate third party user registration and authentication.
    Python Version: 3.6.7
'''


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Movie
import datetime

engine = create_engine('sqlite:///moviecatalog.db')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user


user1 = User(name="User1", email="user1@hotmail.com")
session.add(user1)
session.commit()

user2 = User(name="User2", email="user2@gmail.com")
session.add(user2)
session.commit()

# Create Categories


category1 = Category(name="Drama", user_id=1)
session.add(category1)
session.commit()

category2 = Category(name="Comedy", user_id=1)
session.add(category2)
session.commit()

category3 = Category(name="Horror", user_id=1)
session.add(category3)
session.commit()

category4 = Category(name="Action", user_id=1)
session.add(category4)
session.commit()

category5 = Category(name="Science Fiction", user_id=1)
session.add(category5)
session.commit()

category6 = Category(name="Cartoon", user_id=1)
session.add(category6)
session.commit()

category7 = Category(name="Romance", user_id=1)
session.add(category7)
session.commit()

category8 = Category(name="Family", user_id=1)
session.add(category8)
session.commit()

category9 = Category(name="Ducumentary", user_id=1)
session.add(category5)
session.commit()

# Create Movie Items


movie1 = Movie(user_id=1, name="The Revenant",
               description="A frontiersman on a fur trading expedition \
               in the 1820s fights for survival after being mauled by \
               a bear and left for dead by members of his own hunting team.",
               date=datetime.date.today(), category_id=1, category=category1)

session.add(movie1)
session.commit()

movie2 = Movie(user_id=1, name="The Hangover",
               description="Three buddies wake up from a bachelor party \
               in Las Vegas, with no memory of the previous night and the \
               bachelor missing. They make their way around the city in order \
               to find their friend before his wedding.",
               date=datetime.date.today(), category_id=2, category=category2)

session.add(movie2)
session.commit()

movie3 = Movie(user_id=1, name="Halloween",
               description="Laurie Strode confronts her long-time foe Michael Myers, \
               the masked figure who has haunted her since she narrowly \
               escaped his killing spree on Halloween night four decades ago.",
               date=datetime.date.today(), category_id=3, category=category3)

session.add(movie3)
session.commit()

movie4 = Movie(user_id=1, name="The Equalizer",
               description="A man believes he has put his mysterious past behind him \
               and has dedicated himself to beginning a new, quiet life. But\
               when he meets a young girl under the control of ultra-violent\
               Russian gangsters, he can't stand idly by - he has to help\
               her.",
               date=datetime.date.today(), category_id=4, category=category4)

session.add(movie4)
session.commit()

movie5 = Movie(user_id=1, name="The Space Between Us",
               description="The first human born on Mars travels to Earth for the first time, \
               experiencing the wonders of the planet through fresh eyes. He\
               embarks on an adventure with a street smart girl to discover\
               how he came to be.",
               date=datetime.date.today(), category_id=5, category=category5)

session.add(movie5)
session.commit()

movie6 = Movie(user_id=1, name="Moana",
               description="In Ancient Polynesia, when a terrible curse incurred by the \
               Demigod Maui reaches Moana's island, she answers the Ocean's\
               call to seek out the Demigod to set things right.",
               date=datetime.date.today(), category_id=6, category=category6)

session.add(movie6)
session.commit()

movie7 = Movie(user_id=1, name="A Star Is Born",
               description="Seasoned musician Jackson Maine discovers and falls in love with \
               struggling artist Ally. She has just about given up on her\
               dream to make it big as a singer until Jackson coaxes her into\
               the spotlight. But even as Ally's career takes off, the\
               personal side of their relationship is breaking down, \
               as Jackson fights an ongoing battle with his own internal\
               demons.",
               date=datetime.date.today(), category_id=7, category=category7)

session.add(movie7)
session.commit()

movie8 = Movie(user_id=1, name="Christopher Robin",
               description="A working-class family man, Christopher Robin, encounters his \
               childhood friend Winnie-the-Pooh, who helps him to rediscover\
               the joys of life.",
               date=datetime.date.today(), category_id=8, category=category8)

session.add(movie8)
session.commit()

movie9 = Movie(user_id=1, name="Our Planet",
               description="To follow up the soothing Planet Earth episodes that made us all \
               ooh and ahh, David Attenborough will be narrating another\
               nature docuseries. This one a deep dive into understanding\
               the rock we all call Earth.",
               date=datetime.date.today(), category_id=9, category=category9)

session.add(movie9)
session.commit()


print("\n*** Populated sample data successfully! ***\n")
