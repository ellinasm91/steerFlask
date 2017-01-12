from FlaskWebProject.steershared.shared_consts import *
from FlaskWebProject.steerapi import crud_safety
from FlaskWebProject.steerapi import sec
import json

_retailers = [{NAME: "Canterbury Exotics", DESCRIPTION: "Pet shop", POSTCODE: "CT1 1BB",
               ADDRESS: "70 Northgate,Canterbury,UK", LONG: 1.0836257999999361, LAT: 51.2826094, EMAIL: "",
               PHONE: "01227 786033", WEBSITE: "http://www.canterburyexotics.co.uk/", IMAGE_URL: ""},
              {NAME: "Elite Beauty", DESCRIPTION: "Beauty Salon", POSTCODE: "CT1 2JA",
               ADDRESS: "20 Orange Street,Canterbury,UK", LONG: 1.0800822999999582, LAT: 51.2804541, EMAIL: "",
               PHONE: 441227451145, WEBSITE: "http://www.elite-beauty-canterbury.co.uk/contact.php", IMAGE_URL: ""},
              {NAME: "The Veg Box Cafe", DESCRIPTION: "Vegetarian Restaurant", POSTCODE: "CT1 2HG", 
               ADDRESS: "17b Burgate,Canterbury,UK", LONG: 1.0834260000000313, LAT: 51.2785581, EMAIL: "",
               PHONE: "01227 456 654", WEBSITE: "http://www.elite-beauty-canterbury.co.uk/contact.php", IMAGE_URL: ""}]


_products = [{RETAILER_ID: "5799d3df5c92eb10ccde802e", NAME: "Granola", DESCRIPTION: "A healthy breakfast",
              PRICE: 3.5, QUANTITY: -1},
             {RETAILER_ID: "5799d3df5c92eb10ccde802e", NAME: "Eggs in Purgatory",
              DESCRIPTION: "A tasty breakfast", PRICE: 4.5, QUANTITY: -1},
             {RETAILER_ID: "5799d3df5c92eb10ccde802e", NAME: "Hot Pot", DESCRIPTION: "A hearty lunch",
              PRICE: 6.0, QUANTITY: -1},
             {RETAILER_ID: "5799d3df5c92eb10ccde802d", NAME: "Waxing Full Leg", PRICE: 20.0, QUANTITY: -1},
             {RETAILER_ID: "5799d3df5c92eb10ccde802d", NAME: "Eyebrow Treatment", PRICE: 12.0,
              QUANTITY: -1},
             {RETAILER_ID: "5799d3df5c92eb10ccde802d", NAME: "Upper Lip Treatment", PRICE: 6.0,
              QUANTITY: -1}]

_recommendations = [{CONSUMER_ID: "5799d3cb5c92eb10ccde802a",
                     ITEM_ID: "5799d5675c92eb11759a3a1a", TYPE: "products",
                     RETAILER_ID: "5799d3df5c92eb10ccde802e", NAME: "Granola",
                     DESCRIPTION: "A healthy breakfast", PRICE: 3.5, RATING: 0.7},
                    {CONSUMER_ID: "5799d3cb5c92eb10ccde802a",
                     ITEM_ID: "5799d5675c92eb11759a3a1b", TYPE: "products",
                     RETAILER_ID: "5799d3df5c92eb10ccde802e", NAME: "Eggs in Purgatory",
                     DESCRIPTION: "A tasty breakfast", PRICE: 4.5, RATING: 0.1},
                    {CONSUMER_ID: "5799d3cb5c92eb10ccde802a",
                     ITEM_ID: "5799d5675c92eb11759a3a1c", TYPE: "products",
                     RETAILER_ID: "5799d3df5c92eb10ccde802e", NAME: "Hot Pot",
                     DESCRIPTION: "A hearty lunch", PRICE: 6.0, RATING: 0.1},
                    {CONSUMER_ID: "5799d3cb5c92eb10ccde802a",
                     ITEM_ID: "5799d5675c92eb11759a3a1d", TYPE: "products",
                     RETAILER_ID: "5799d3df5c92eb10ccde802d", NAME: "Waxing Full Leg", PRICE: 20.0,
                     RATING: 0.2},
                    {CONSUMER_ID: "5799d3cb5c92eb10ccde802a",
                     ITEM_ID: "5799d5675c92eb11759a3a1e", TYPE: "products",
                     RETAILER_ID: "5799d3df5c92eb10ccde802d", NAME: "Eyebrow Treatment", PRICE: 12.0,
                     RATING: 0.5},
                    {CONSUMER_ID: "5799d3cb5c92eb10ccde802a",
                     ITEM_ID: "5799d5675c92eb11759a3a1f", TYPE: "products",
                     RETAILER_ID: "5799d3df5c92eb10ccde802d", NAME: "Upper Lip Treatment", PRICE: 6.0,
                     RATING: 0.2}]


def dummy_create(collection_id):
    docs = globals()['_' + collection_id]
    if collection_id == RETAILER_USERS:
        salt = sec.gen_salt()
        hashed_pass, salt = sec.gen_hashed_pass('Spot1234', salt)
        docs[0][HASHED_PASS] = hashed_pass
        docs[0][SALT] = salt
    new_docs = crud_safety.create(collection_id, docs)
    print new_docs
    return json.dumps(new_docs)


if __name__ == '__main__':
    dummy_create(RETAILER_USERS)
