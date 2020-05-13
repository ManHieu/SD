import mysql.connector
from mysql.connector import errorcode
import re
import pickle
from model.classify.eval import *

class FindDogType():
    def __init__(self, database_url, model_path, class_name_path):
        self.types = []
        self.class_names = pickle.load(open('.\\class_names.pkl', 'rb'))
        self.model, _ = load_model('dog_classification_resnet.pth', self.class_names)
        self._get_all_type(database_url)
    
    def _get_all_type(self, database_url):
        
        try:
            cnx = mysql.connector.connect(user='root', password='270898', 
                                        host='localhost', database='muti_media_db')
            cursor = cnx.cursor()
            query = ("SELECT type FROM dog_type")
            cursor.execute(query)
            types = [line[0] for line in cursor]
            self.types = types
            
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            cnx.close()
        
    def find_dog_type(self, img=None, tag=None):
        tag = []
        img = []
        
        if tag != None:
            tag = self._find_dog_type_from_tag(tag)

        if img != None:
            img =  self._find_dog_type_from_img(img)
        
        result = set(tag).intersection(set(img))
        return result
        

    def _find_dog_type_from_img(self, img):
        types = predict(self.model, self.class_names, img)
        return types

    def _compare_str(self, str1, str2):
        score = sum(c1!=c2 for c1, c2 in zip(str1, str2)) + + abs(len(str1) - len(str2))
        return score

    def _find_dog_type_from_tag(self, tag):
        tag = re.sub(r'\W+','', tag).lower()
        scores = []
        for typ in self.types:
            normal_typ = re.sub(r'\W+','', typ).lower()
            score = self._compare_str(tag, normal_typ)
            scores.append((typ, score))
        scores.sort(key=lambda x: x[1], reverse=True)[:5]
        return [typ for (typ, score) in scores]
