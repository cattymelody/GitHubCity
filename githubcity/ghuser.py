#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module allow to developers to get all some data about a given GitHub user.

Author: Israel Blancas @iblancasa
Original idea: https://github.com/JJ/github-city-rankings
License:

The MIT License (MIT)
    Copyright (c) 2015 Israel Blancas @iblancasa (http://iblancasa.com/)

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software
    and associated documentation files (the “Software”), to deal in the Software without
    restriction, including without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom
    the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or
    substantial portions of the Software.

    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
    PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
    FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
    IN THE SOFTWARE.

"""
import time
from bs4 import BeautifulSoup
import urllib.request
from urllib.error import HTTPError, URLError
import datetime, dateutil.parser
from dateutil.relativedelta import relativedelta
import re

class GitHubUser:
    """Manager of a GitHub User

    Attributes:
        _name (str): Name of the user (private).
        _contributions (int): total contributions of a user in the last year (private).
        _followers (int): total number of followers of an user (private).
        _numRepos (int): number of repositories of an user (private).
        _stars (int): number of total stars given to the user (private).
        _organizations (int): number of public organizations where the user is (private).
        _join (str): when the user joined to GitHub. Format: %Y-%M-%DT%H:%i:%sZ (private).
        _avatar (str): URL where the user's avatar is (private).
        _language (str): language most user by the user (private).
        _bio (str): bio of the user (private).
    """

    def __init__(self, name, server="https://github.com/"):
        """Constructor of the class.
        Args:
            name (str): name (login) of an user in GitHub
            server (str): server to query data. Default: https://github.com/

        Returns:
            a new instance of GitHubUser class
        """
        self._name = name
        self._server = server

    def export(self):
        """Export all attributes of the user to a dict
        Returns:
            dict with all attributes of the user
        """
        data = {}
        data["name"] = self.getName()
        data["contributions"] = self.getContributions()
        data["language"] = self.getLanguage()
        data["avatar"] = self.getAvatar()
        data["followers"] = self.getFollowers()
        data["join"] = self.getJoin()
        data["organizations"] = self.getOrganizations()
        data["repositories"] = self.getNumberOfRepositories()
        data["stars"] = self.getStars()
        data["bio"] = self.getBio()
        return data


    def getName(self):
        """Get the name of the user
        Returns:
            str with the name of the user
        """
        return self._name

    def getContributions(self):
        """Get the number of public contributions of the user
        Returns:
            int with the number of public contributions of the user
        """

        return self._contributions

    def getLanguage(self):
        """Get the most used language by the user

        Returns:
            str with the language most used

        """
        return self._language

    def getAvatar(self):
        """Get the URL where the avatar is

        Returns:
            str with an URL where the avatar is
        """
        return self._avatar

    def getFollowers(self):
        """Get the number of followers of this user

        Returns:
            int with the number of followers
        """
        return self._followers

    def getLocation(self):
        """Get the location of the user

        Returns:
            str with location of the user
        """
        return self._location

    def getJoin(self):
        """Get when an user joined to GitHub

        Returns:
            a str with this time format %Y-%M-%DT%H:%i:%sZ
        """
        return self._join

    def getOrganizations(self):
        """Get the number of public organizations where the user is

        Returns:
            int with the number of organizations

        """
        return self._organizations

    def getNumberOfRepositories(self):
        """Get the number of repositories of this user

        Returns:
            int with the number of repositories
        """
        return self._numRepos

    def getStars(self):
        """Get number of stars given from GitHub users to repositories created by this user

        Returns:
            int with the number of stars
        """
        return self._stars

    def getBio(self):
        """Get the bio of the user

        Returns:
            str with the bio
        """
        return self._bio 

    def getData(self, debug = False):
        """Get data of a GitHub user.
        """
        if not debug:
            url = self._server + self._name
            data = self._getDataFromURL(url)
            web = BeautifulSoup(data,"lxml")

            contributions_raw = web.find_all('div',{'class':'boxed-group flush'})
            self._contributions = int(contributions_raw[2].text.split(" ")[6].replace(",",""))

            #Language

            self._language = web.find("meta", {"name":"description"})['content'].split(" ")[6]
            if self._language[len(self._language)-1]==",":
                self._language = self._language[:-1]

            #Avatar
            self._avatar = web.find("img", {"class":"avatar"})['src'][:-10]

            #Followers
            vcard = web.find_all("strong", {"class":"vcard-stat-count"})
            if "k" in vcard[0].text:
                self._followers = int(float(vcard[0].text[:-1].replace('\.',','))*1000)
            else:
                self._followers = int(vcard[0].text)

            #Location
            self._location = web.find("li", {"itemprop":"homeLocation"}).text

            #Date of creation
            join = dateutil.parser.parse(web.find("local-time",{"class":"join-date"})["datetime"])
            self._join = join.strftime("%Y-%m-%d %H:%M:%S %Z")

            #Number of organizations
            self._organizations = len(web.find_all("a",{"class":"avatar-group-item"}))

            #Number of repos
            url +="?tab=repositories"
            data = self._getDataFromURL(url)
            web = BeautifulSoup(data,"lxml")

            repos = web.find_all("a",{"aria-label":"Stargazers"})
            self._numRepos = (len(repos))

            #Number of total stars
            stars = 0
            non_decimal = re.compile(r'[^\d]+')

            for repo in repos:
                stars += int(non_decimal.sub('', repo.text))

            self._stars = stars

            bio = web.find_all("div",{"class":"user-profile-bio"})
            self._bio = bio[0].text

        else:
            self._contributions = 1000
            self._language="Python"
            self._avatar =""
            self._followers = 1
            self._join = "2013-06-24"
            self._organizations = 1
            self._numRepos = 1
            self._stars = 1
            self._location = "Barcelona"
            self._bio ="Bio"

    def getRealContributions(self):
        datefrom = datetime.datetime.now() - relativedelta(years=1)
        dateto = datefrom + relativedelta(months=1) - relativedelta(days=1)

        public = 0
        private = 0

        while datefrom < datetime.datetime.now():
            fromstr = datefrom.strftime("%Y-%m-%d")
            tostr = dateto.strftime("%Y-%m-%d")
            url = "https://github.com/"+self._name+"?tab=overview&from="+fromstr+"&to="+tostr
            data = self._getDataFromURL(url)
            web = BeautifulSoup(data,"lxml")
            ppcontributions = web.find_all('span',{'class':'text-emphasized'})



            print(url)

            if len(ppcontributions) == 3:
                public+=int(ppcontributions[0].text.replace(",",""))
                private += int(ppcontributions[2].text.split(" ")[10])
                
                print(int(ppcontributions[0].text.replace(",","")))
                print(int(ppcontributions[2].text.split(" ")[10]))


            elif len(ppcontributions) == 2:
                if ppcontributions[0].parent.text.split(" ")[1] =="commits\n":
                    public+=int(ppcontributions[0].text)
                    print(int(ppcontributions[0].text))
                if ppcontributions[1].parent.text.split(" ")[20] == "contributions\n":
                    private += int(ppcontributions[1].text.split(" ")[10])
                    print(int(ppcontributions[1].text.split(" ")[10]))
            elif len(ppcontributions)==1:
                if ppcontributions[0].parent.text.split(" ")[1] =="commits\n":
                    public+=int(ppcontributions[0].text)
                    print(int(ppcontributions[0].text))
                elif ppcontributions[0].parent.text.split(" ")[20] == "contributions\n":

                    print(ppcontributions[0].text.split(" ")[10])
                    private += int(ppcontributions[0].text.split(" ")[10])
                    print(int(ppcontributions[0].text.split(" ")[10]))

            datefrom += relativedelta(months=1)
            dateto += relativedelta(months=1)

        print(public)
        print(private)
        print(public+private)
       


    def _getDataFromURL(self, url):
        """Read HTML data from an user GitHub profile (private).

        Note:
            This method is private.
            If max number of request is reached, method will stop some time.

        Args:
            url (str): URL to query.

        Returns:
            A str with the webpage
        """
        code = 0

        hdr = {'User-Agent': 'curl/7.43.0 (x86_64-ubuntu) libcurl/7.43.0 OpenSSL/1.0.1k zlib/1.2.8 gh-rankings-grx',
               'Accept': 'text/html'
               }

        while code != 200:
            req = urllib.request.Request(url, headers=hdr)
            try:
                response = urllib.request.urlopen(req)
                code = response.code
                time.sleep(0.01)
            except HTTPError as e:
                code = e.code
                if code == 404:
                    break;
            except URLError as e:
                time.sleep(3)

        if code == 404:
                raise Exception("User was not found")
        return response.read().decode('utf-8')
