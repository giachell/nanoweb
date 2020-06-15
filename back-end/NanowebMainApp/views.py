from django.shortcuts import render, redirect
from django.http import JsonResponse
from bs4 import BeautifulSoup
import psycopg2
from psycopg2 import sql
import json
import requests
import string
import os
import redis
from .models import Query
from .forms import QueryForm


# NanoWeb views here.

# NOTE: confidential values are replaced with asterisks: ***

def index(request):
    """Home page for NanowebMainApp (and project)"""
    return render(request, 'NanowebMainApp/index.html')

def about(request):
    """About page for NanowebMainApp (and project)"""
    return render(request, 'NanowebMainApp/about.html')

def stats_json(request):
    """Stats JSON for NanowebMainApp (and project)"""
    try:
        connection = psycopg2.connect(user = ***, password = ***, host = ***, port = ***, database = ***)

        cursor = connection.cursor()

        stmt = sql.SQL("""
                       SELECT COUNT(*) AS NN FROM nanopublication;
                   """)

        print(stmt)

        cursor.execute(stmt)


        jsonDict = {}
        n_nanopubs = 0
        n_triples = 0


        for record in cursor:
            n_nanopubs = record[0]
            break
        n_triples = int(n_nanopubs * 38.5);

        jsonDict["n_nanopubs"] = n_nanopubs
        jsonDict["n_triples"] = n_triples


    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()


    return JsonResponse(jsonDict)

def stats(request):
    """Stats page for NanowebMainApp (and project)"""
    return render(request, 'NanowebMainApp/stats.html')

def query(request, queryText):
    """Query page for NanowebMainApp (and project)"""
    context = {'queryText': queryText}
    return render(request, 'NanowebMainApp/query.html', context)


def queries(request):
    """Query list page for NanowebMainApp (and project)"""
    query_list = Query.objects.all();
    context = {'queries': query_list}
    return render(request, 'NanowebMainApp/queries.html', context)

def results(request, queryText):
    """Results page for NanowebMainApp (and project)"""
    query = queryText.replace("§", "/")
    form = QueryForm(initial={'text': query})
    context = {'queryText': query, 'form':form}
    return render(request, 'NanowebMainApp/results.html', context)

def nanopubinfo(request, nanopubIdentifier):
    """Nanopubinfo page given the nanopubIdentifier for NanowebMainApp (and project)"""
    context = {'nanopubIdentifier': nanopubIdentifier}
    return render(request, 'NanowebMainApp/nanopubinfo.html', context)

def nanopub(request, nanopubIdentifier):
    """Nanopubinfo data given the nanopubIdentifier for NanowebMainApp (and project)"""
    nanopub_list_json = '/locale/data/nanopub/list/JSON/list.json'
    dict = {}
    response = ""
    path_original = ""
    path_new = ***
    response_json = {"init":""}
    print(nanopubIdentifier)
    host_var = ***
    port_var = ***
    # Connect to our Redis instance
    redis_instance = redis.StrictRedis(host=host_var,
                                       port=port_var, db=0)

    path_original = redis_instance.get(nanopubIdentifier).decode()

    print("path_original: '"+str(path_original)+"'")
   
    url = 'http://localhost:8080/nanocitationandindexing/rest/jsonmeta/dbindex'

    payload = "{trigfile: '"+str(path_original)+"'}"

    x = requests.post(url, data=payload)
    # GET the JSON, retrive evidence and print JSON:

    response_json = x.json()
    evidence = {}
    evidence["name_type"] = "prova evidence.name_type"
    evidence["title"] = "prova evidence.title"
    evidence["type"] = "prova evidence.type"
    evidence["id"] = response_json["evidenceReferences"][0]["id_evid"]
    id_evid = evidence["id"]

    # Retrive evidence info
    try:
        connection = psycopg2.connect(user = ***, password = ***, host = ***, port = ***, database = ***)

        cursor = connection.cursor()
        sql = f"SELECT * FROM evidence WHERE id_evid='{id_evid}'"
        cursor.execute(sql)

        for record in cursor:
            evidence["type"] = record[1]
            evidence["name_type"] = record[2]
            evidence["title"] = record[3]
            evidence["abstract"] = record[4]

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()

    response_json["evidenceProps"] = evidence


    #Try to retrieve collaborators "name" and "family_name"

    if("collaborators" in response_json.keys()):
        collaborators = response_json["collaborators"]


        cc = 0
        for collaborator in collaborators:
            if "name" in collaborator.keys() and "family_name" in collaborator.keys() or collaborator['type_agent'] == 'ORGANISATON':
                continue
            else:
                # Retrieve info
                id_agent = collaborator["id_agent"]
                html = requests.get(id_agent)
                print(html.text)
                soup = BeautifulSoup(html.text, "html.parser")
                elements = soup.find_all("title")
                print("elements: "+str(elements))
                name = ""
                for element in elements:
                    name_texts = element.contents[0].replace("  | Publons", "").split()
                    collaborators[cc]["name"] = name_texts[0]
                    collaborators[cc]["family_name"] = name_texts[1]
            cc += 1







    return JsonResponse(response_json, safe=False)

def search(request):
    """Search page for NanowebMainApp (and project)"""

    if request.method != 'POST':
        # No data submitted -> create a blank form.
        form = QueryForm()
    else:
        # POST data submitted -> fill the form with data.
        form = QueryForm(data=request.POST)
        if form.is_valid():
            form.save()
  
            query = request.POST.__getitem__("text")

            return redirect('NanowebMainApp:results', queryText=query)

    context = {'form': form}
    return render(request, 'NanowebMainApp/search.html', context)

def querysuggestions(request, queryText):
    """Query suggestions page for NanowebMainApp (and project)"""
    try:
        connection = psycopg2.connect(user = ***, password = ***, host = ***, port = ***, database = ***)

        cursor = connection.cursor()

        queryText = queryText.replace("§","/");

        print(queryText)

        stmt = sql.SQL("""
                    SELECT description FROM assertion_content WHERE LOWER(description) LIKE LOWER({queryText}) LIMIT 15;
                """).format(
            queryText=sql.Literal('%'+queryText+'%'),
        )

        print(stmt)

        cursor.execute(stmt)
        suggestionsList = []
        for record in cursor:
            temp = record[0].replace("'","")
            if ("[" in temp and "]" in temp):

                leftSquareBracketPos = temp.index("[")
                rightSquareBracketPos = temp.index("]")
                patternToRemove = temp[leftSquareBracketPos:rightSquareBracketPos + 1]
                temp = temp.replace(patternToRemove, "").lstrip()
            else:
                print("No replace done")

            suggestionsList.append(temp)

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()

            suggestionsListDict = {'suggestionsList':suggestionsList}


    return JsonResponse(suggestionsListDict)

def nanopubs(request, query):


    url = 'http://exa.dei.unipd.it:8080/nanocitationandindexing/rest/query/'

    # remove single and double quotes
    query = query.replace('"','').replace("'","")
    print("Query: "+query)

    #connect to db to check if query is a nanopub ID
    id_np = None
    try:
        connection = psycopg2.connect(user = ***, password = ***, host = ***, port = ***, database = ***)

        cursor = connection.cursor()
        stmt = "SELECT id_np FROM nanopublication WHERE id_np = '"+query+"' LIMIT 100;"
        print("STATEMENT:\n"+stmt)
        cursor.execute(stmt)

        for record in cursor:
            id_np = record[0]
            break
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()

    query = query.rstrip(string.punctuation)

    x = requests.post(url, data=query)



    nanopubs_demo_list = [

        "RAF-sSeIJLYyhpjuOy-pUFkipOavZb2JB1HpAaJaPH0_8",
        "RAF-q6M7ske_tfUAw165iIH26pSQOPJo6A_M9nMbRRO4E",
        "RAF-sYhUYv7FOhu4iFTJRs9L6U0CH2XfJZkV477F8b12c",
        "RAF-sdEeT3YjI1ztM8OU386t9jPszn2_lw6Q4h_Z935no",
        "RAF-saFJWA6Fu6BPDNBFQr1JAVXwDrKSkx2nBqoxHXumQ",
        "RAF-sGYYt8peG-V2J6nQpB05g94AtVoIiMhYIAW6ILuTE",
        "RAF-sf0fwb9OJP0PAGdrjAx1ZPJRmqLFfvggL9cmOMTyw",
        "RAEzj4ewTY1tiyisVw23KUD93aFT0q9vL3-Rw-6vE2-KA",
        "RAF-sj-cNDXADcFetLuLBihjfZfJMeH_ScMY4pysAD2KQ",
        "RAF-slmuO-vw36nvjPBj1KXJYZyqmYvnommtIhmWcExMM",
        "RAF-szeOOdn27DCkHE7neO-UeytVY3mIDk6D8z4hU1u8A",
        "RAF-sr7-5A756yyQoh3A3d2bLnSqAq7BLFoZwzIpRr9kw",
        "RAF-sT4KV4gXOZPP4byjlF637V0st90DbSdqr9pE7oYMA",
        "RAF-se3B72CTb3AC4KuJWSjmFkz48rctb1rS8-VTsInRQ",
        "RAF-tEiiDKw5w3XwPBuBhC-0AiYxQTl4VK8ID0SiVaklg",
        "RAF-t7b7mMsHH8Bri76_BMi5bHPvAZhH3f1TlBlceIO4g",
        "RAF-tB7pPMMxvDQ2jhDmWrLlve6wI3hGoAl8KYlQYKj1o",
        "RAF-tFfxfZhT0Mv0AEw2X8S99ZaXNMurn4cLr2B84kftw",
        "RAF-slsHBAWVBIagnFxWEQ5-HDFkVQFQ6db5g9dPRkOZo",
        "RAF-gTTl_tJRH_ftlTo12c3spJ6SrWNUXPi8GmSyysrrU"
    ]

    response_json = x.json()


    if "cancer" in query and "0" in response_json.keys():
        del response_json["0"]
        


    list_nanopubs = list(response_json.values())
   
    cut_off = 200  # avoid a very long response JSON array
    list_nanopubs = list_nanopubs[0:cut_off]

    if (id_np != None):
        print("Entered in if (id_np != None): ")
        list_nanopubs.insert(0, id_np)
        response_json = {}

        counter = 0
        for np in list_nanopubs:
            response_json[counter] = np
            counter += 1


    return JsonResponse(response_json, safe=False)


def node_linked_elements(request, node):
    """Node linked elements for a node of NanowebMainApp (and project)"""
    try:
        connection = psycopg2.connect(user = ***, password = ***, host = ***, port = ***, database = ***)

        cursor = connection.cursor()

        node = node.replace("§","/")
        node = node.lower()

        stmt = "SELECT description, subject FROM assertion_content WHERE LOWER(description) LIKE '%"+node+"%' LIMIT 100;"

        print("STATEMENT:\n"+stmt)


        cursor.execute(stmt)
        list_of_linked_elements = []
        list_of_linked_elements_txt_only = []
        for record in cursor:
            temp = record[0].replace("'","")
            print("temp:"+temp)
            if("[" in temp and "]" in temp):
                leftSquareBracketPos = temp.index("[")
                rightSquareBracketPos = temp.index("]")
                patternToRemove = temp[leftSquareBracketPos:rightSquareBracketPos+1]
                temp = temp.replace(patternToRemove,"").lstrip()
            record_items = temp.split(' - ')
            print(record_items)
            counter = 0
            if(node in record_items[0].lower() or node in record_items[1].lower()):
                for record_item in record_items:
                    if( (len(list_of_linked_elements_txt_only) < 15) and (node not in record_item.lower()) ):
                        if(record_item.strip() not in list_of_linked_elements_txt_only):
                            list_of_linked_elements_txt_only.append(record_item.strip())
                            if(counter<1):
                                list_of_linked_elements.append({"text": record_item.strip(), "role": "subject", "predicate": record[1]})

                            else:
                                list_of_linked_elements.append({"text": record_item.strip(), "role": "object", "predicate": record[1]})
                    counter+=1

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
            dict_of_linked_elements = {'list_of_linked_elements':list_of_linked_elements}
            print(dict_of_linked_elements)

    return JsonResponse(dict_of_linked_elements)


def entity_properties(request, entity):
    """Node linked elements for a node of NanowebMainApp (and project)"""
    try:
        connection = psycopg2.connect(user = ***, password = ***, host = ***, port = ***, database = ***)
        cursor = connection.cursor()
        entity = entity.replace("§", "/")
        entity_properties = {}
        stmt = sql.SQL("""
                         SELECT * FROM entity WHERE entity.name = {entity}
                     """).format(
            entity=sql.Literal(entity),
        )

        cursor.execute(stmt)

        for record in cursor:
            entity_properties["id_entity"] = record[0]
            entity_properties["type"] = record[1]
            entity_properties["name"] = record[2]
            entity_properties["symbol"] = record[3]
            entity_properties["description"] = record[4]


    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

            print(entity_properties)

    return JsonResponse(entity_properties)


def nanopub_related_to(request, source, target):
    """Nanopub related to source and target of NanowebMainApp (and project)"""
    try:
        connection = psycopg2.connect(user = ***, password = ***, host = ***, port = ***, database = ***)

        cursor = connection.cursor()

        host_var = ***        
        port_var = ***
        path_original = ""

        # Connect to our Redis instance
        redis_instance = redis.StrictRedis(host=host_var,
                                           port=port_var, db=0)

        source = source.replace("§", "/")
        target = target.replace("§", "/")

        bow_source = source.split(" ")
        bow_target = target.split(" ")
        first_bow_source = bow_source[0]
        first_bow_target = bow_target[0]

        
        stmt = sql.SQL("""
                         SELECT * FROM assertion_content WHERE LOWER(description) LIKE LOWER({association})
                      """).format(
            association=sql.Literal("%"+source+"% - %"+target+"%")
        )
        cursor.execute(stmt)

        for record in cursor:

            id_assertion_temp = record[0]
            pos_last_slash = id_assertion_temp.rfind("/")
            pos_np = pos_last_slash + 1
            id_assertion_temp = id_assertion_temp[pos_np:]

            id_assertion_temp = id_assertion_temp.replace("#assertion", "")
            id_assertion_temp = id_assertion_temp.replace(".assertion", "")
            id_assertion_temp = id_assertion_temp.replace("_assertion", "")
            id_assertion_temp = id_assertion_temp.replace("#trig", "")
            id_assertion_temp = id_assertion_temp.replace("trig#", "")
            pos_last_dot = id_assertion_temp.rfind(".")
            pos_np = pos_last_dot + 1

            id_np = id_assertion_temp[pos_np:]

            print(id_np)

            try:
                path_original = redis_instance.get(id_np).decode()
                nanopub_ids["id_np"] = id_np
                break
            except AttributeError:
                print("Nanopublication with id: "+id_np+" does NOT exists!")

        if path_original == "":

            two_words_source = ""
            two_words_target = ""
            if len(bow_source) >= 2:
                two_words_source = first_bow_source + " " + bow_source[1]
            if len(bow_target) >= 2:
                two_words_target = first_bow_target + " " + bow_target[1]

            if two_words_source:
                source_to_use = two_words_source
            else:
                source_to_use = first_bow_source

            if two_words_target:
                target_to_use = two_words_target
            else:
                target_to_use = first_bow_target

            stmt = sql.SQL("""
                             SELECT * FROM assertion_content WHERE LOWER(description) LIKE LOWER({association})
                          """).format(
                association=sql.Literal("%" + source_to_use + "% - %" + target_to_use + "%")
            )
            cursor.execute(stmt)

            print("statement con bow: "+stmt.as_string(connection))

            for record in cursor:

                id_assertion_temp = record[0]
                pos_last_slash = id_assertion_temp.rfind("/")
                pos_np = pos_last_slash + 1
                id_assertion_temp = id_assertion_temp[pos_np:]

                id_assertion_temp = id_assertion_temp.replace("#assertion", "")
                id_assertion_temp = id_assertion_temp.replace(".assertion", "")
                id_assertion_temp = id_assertion_temp.replace("_assertion", "")
                id_assertion_temp = id_assertion_temp.replace("#trig", "")
                id_assertion_temp = id_assertion_temp.replace("trig#", "")
                pos_last_dot = id_assertion_temp.rfind(".")
                pos_np = pos_last_dot + 1

                id_np = id_assertion_temp[pos_np:]

                print(id_np)

                try:
                    path_original = redis_instance.get(id_np).decode()
                    nanopub_ids["id_np"] = id_np
                    break
                except AttributeError:
                    print("Nanopublication with id: " + id_np + " does NOT exists!")



    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


        url = 'http://localhost:8080/nanocitationandindexing/rest/jsonmeta/dbindex'

        if path_original:
            payload = "{trigfile: '" + str(path_original) + "'}"
            x = requests.post(url, data=payload)
            response_json = x.json()
        else:
            response_json ={'error':'No reference found'}
        print("response_json" + str(response_json))

        return JsonResponse(response_json, safe=False)