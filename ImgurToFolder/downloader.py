# Python modules
import imgurpython as ip
import requests
import os

# Dev defined modules
import config

class Downloader:
    def __init__(self, client_id, client_secret, folder_path):
        self.client = ip.ImgurClient(client_id, client_secret)
        self.desired_folder_path = self.check_folder_path(folder_path)

    def parse_for_gallery_id(self, url):

        # Base url path for gallery and album
        # If base url path ever changes only need to change these two variables
        album = 'imgur.com/a/'
        gallery = 'imgur.com/gallery/'

        # Must start as -1 as a 'NULL'
        start_position = -1

        if url.find(album) != -1:
            start_position = int( url.find(album) + len(album) )

        elif url.find(gallery) != -1:
            start_position = int( url.find(gallery) + len(gallery) )

        if start_position != -1:
            end_position = int (url.find('/', start_position) )
            if (end_position > -1):
                return url[start_position:end_position]
            else:
                return url[start_position:]
        else:
            return None

    def replace_characters(self, word):
        # NOTE: '\\/:*?"<>|.' are invalid folder characters in a file system
        invalid_characters = ['\\','/',':','*','?','"','<','>','|','.']
        for character in invalid_characters:
            word = word.replace(character, '')

        return word

    def check_folder_path(self, path):
        """ Checks if the last char of the path has a '/' to complete the extension """
        path = path.replace('\\','/')

        if path[-1:] != '/':
            path += '/'
        return path

    def download_album(self, url = ''):
        ID = self.parse_for_gallery_id(url)

        if ID == None:
            print ('ERROR: No album link given')
            return

        album_title = self.client.get_album(ID).title

        if album_title == None:
            album_title = ID

        print ('Downloading album:', album_title, end='', flush=True)

        # If not album
        try:
            for position, image in enumerate (self.client.get_album(ID).images):
                self.download_image(image['link'], album_title, position + 1)
            
            print (' - [FINISHED]')    
        # Then it's a gallery
        except ip.helpers.error.ImgurClientError:
            self.download_image ( self.client.gallery_item(ID).link, album_title )
            print (' - [FINISHED]')

        # Knwon bug in imgurpython
        except Exception as e:
            print ('\nERROR:', url, 'has failed!', e)
            
            
        

    def download_image(self, url = '', directory_name = None, album_position = 0):

        req = requests.get(url, stream = True)

        if req.status_code == 200:

            #Link names
            if album_position == 0:
                link_name = url[url.rfind('/') + 1:]
            else:
                # First erase invalid characters
                link_name = directory_name + ' - ' + str( album_position )
                link_name = self.replace_characters(link_name)

                # Then add file_extension
                file_extension = url[url.rfind('.'):]
                link_name += file_extension

            # If directory_name is given, make it the new folder name
            if directory_name != None:

                directory_name = self.replace_characters(directory_name)
                directory_name = self.desired_folder_path + directory_name
                directory_name = self.check_folder_path(directory_name)


            # Else make the desired_folder_path the folder to download in
            elif config.enable_single_images_folder:
                directory_name = self.desired_folder_path + 'Single-Images/'

            else:
                directory_name = self.desired_folder_path

            # Check if directory exists
            if not os.path.exists(directory_name):
                os.makedirs(directory_name)


            with open(directory_name + link_name, 'wb') as image_file:
                for chunk in req:
                    image_file.write(chunk)


    def change_folder(self, folder_path):
        self.desired_folder_path = self.check_folder_path(folder_path)