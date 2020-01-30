# OpenStax CMS Documentation

## General
* Overall design concept - The CMS is designed to house and make available data needed by the OpenStax.org (OS) Site frontend. All of the data is available via a REST API. Since the OS site is a marketing site, we need the ability to change images or wording quickly and easily without a code release. Editing the CMS provides this functionality.
* [API Endpoints](https://github.com/openstax/openstax-cms/wiki/API-Endpoints)
* [Import data into local database](https://github.com/openstax/openstax-cms/wiki/Import-database-dump-into-local-env)

## CMX Django Application Details

### Accounts
* Used for accounts in dev and local environments
* Will not be used for any environment using Cloudfront since Cloudfront redirects /accounts to OS Accounts.
* The CMS database contains many users because when the app was first deployed, user info was stored in the CMS. That functionality is now in OS Accounts.

### Admin Templates
* Contains templates for Wagtail login and for adding a redirect URL.
* The Redirect template is used to add Javascript to add validation that the URL contains a `/l/` or `/r/`
* Redirect URLs are used in books and are short openstax URLs used for third party sites
* Redirects are available from the Settings menu

### Allies
* Model for the Partners page
* It was originally called the Ally page
* Each Ally has one or more subjects they cover. The list can be filtered by subject in the OS UI.
* They also fall into 3 possible categories: Online homework, Adaptive courseware and Customization tools
* The Partner data is pulled from Salesforce. See [Salesforce section](#Salesforce)

### API
* APIs for various data
  * images - images used on OS site. Images are defined here to add the URL to the image, since it's stored on cloudfront. It reduces one API call for the FE. 
  * documents - PDFs, PowerPoints, text files, etc. SVGs are also under documents since they are not considered images by Wagtail.
  * adopters - 
  * progress - an API to hold progress for the adoptor quiz. The FE writes progress to it and retrieves it when needed.
  * sticky note - a time limited banner that displays at the top of the site
  * schools - list of schools using OpenStax books. Used for map display on OS site. Data comes from Salesforce
  * mapbox - data for mapbox. Data comes from Salesforce
  * flags - not sure what this is for
  * errata-fields - errata data
  * footer - data for site footer

### Books
* APIs and models for Book information
* API allows getting information for all books or a single book

### Duplicate Books
* Form that, once completed, allows for the duplication of book data into a new book model
* Uses Wagtail import-export package

### Errata
* seperate Django app that is used for handling errata through a workflow. The app does not use Wagtail as does the rest of OS CMS.
* Uses standard Django templates for the user interface
* The workflow is a series of states
  * New
  * Editorial review
  * Reviewed
  * Archived
  * Completed
* Errata is entered via a form on the OS site. Users can choose to be updated via email on the status of their entry. Emails are sent as the status changes.
* Users can also view errata on the OS site. Data is available via an API.
* Errata can have various resolutions
  * Duplicate
  * Not An Error
  * Will Not Fix
  * Approved
  * Major Contains code for the BlogBook Revision
  * Technical Error
  * Sent to Customer Support
  * More Information Requested
* Errata can be various error types
  * Other factual inaccuracy in content
  * General/pedagogical suggestion or question
  * Incorrect answer, calculation, or solution
  * Broken link
  * Typo
  * Other
* Emails are sent to users who entered the errata as it moves through the workflow. 
* Errata can be filtered in the UI

### Extra Admin Filters
* Used to filter errata
* Allows users to filter multiple books in the same query

### Global Settings
* Views and models for items on the Admin Settings menu
  * Sticky Note
  * Footer
  * Cloudfront Distribution - this holds a cloudfront distribution id. When it's filled in, a call is made to dump the cache of cloudfront for this distribution on each wagtail page save (using a post-save hook). This is not currently in use because REX has not figured out all the details needed. 

### Mail
* Used to send the redirect report email to the Content team
* Used for the contact form in the OS UI.
* There could be some dead code in this app

### News
* Contains code for the Blog Atom feed
* Contains code for blog posts
* Has APIs for a full list of blog posts or an single blog post
* Contains code for OS press kit
* Search is implemented for blog posts

### OpenStax
* The application used for settings and general items
* APIs for accessing Documents and Images
* Document API checks if faculty documents should be hidden or not. This is the one feature with a feature flag in the CMS.
* Routing for other APIs

### OXAuth
* Handles OAuth between CMS and OS Accounts
* Has APIs for login, logout and user info. The user info API is not used in the OS app. It gets user info from the OS acccounts API

### Pages
* Models, APIs and views for all pages related to the OS site
* Each page has a unique set of fields, images and/or documents.
* All of the pages are children of the Homepage.
* Has template for general pages that can be used for short term pages on the OS site

### Redirects
* Has management command that checks if all the redirect URLs return a 201. It creates a list of all failures and emails the list to the content team.
* The command is run on the first of each month via a cron job

### Salesforce
* Used to pull data from Salesforce
  * Adopter
  * Faculty status
  * Partners
  * Schools and mapbox data
  * Opportunities
* Used to upload school data to mapbox
* Uses SimpleSalesforce to connect to Salesforce API
* Opportunities are used for the renewal form which users are asked to update after a period of time.

### Snippets
* Snippets are objects that can be reused on pages for specific content
* They can be created, edited or removed in the Admin interface
* Current snippets are
  * Subject
  * Faculty Resourse
  * Student Resource
  * Role
  * Shared Content
  * News Source
* There are APIs for Roles and Subjects

## Other
* **Import-Export:** Admin has a feature to import or export a page. This uses the [Wagtail import-export package](https://pypi.org/project/wagtail-import-export-tool/). It is used to move pages from one environment to another.

## Database
Below is a link to an image of the database scema as of 1-13-2020. The image might need to be downloaded for proper viewing.

[Database Schema image](openstax-cms-db.png)