#!/usr/bin/env python3

'''
    File name: database_setup.py
    Author: Khalid Saleem
    Date created: 08/03/2019
    Date last modified: 28/03/2019
    Description: to create a database structure for a web application that
    provides a list of items within a variety of categories and integrate third
    party user registration and authentication.
    Python Version: 3.6.7
'''

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# Class to create User table structure


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
            }


# Class to create Category table structure


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
        }


# Class to create Movie items table structure


class Movie(Base):
    __tablename__ = 'movie'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    date = Column(DateTime)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'date': self.date,
            'category_id': self.category_id,
            'category': self.category.name,
            'user_id': self.user_id,
        }


engine = create_engine('sqlite:///moviecatalog.db')


Base.metadata.create_all(engine)
