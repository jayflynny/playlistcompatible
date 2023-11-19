from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import json
import csv
#Creates and returns a list of the ids from the playlist info
def idlist(playlist_info):
    playlist_list = playlist_info.split(',')
    ids=[]
    for ind, x in enumerate(playlist_list):
        if '"id":' in x:
            ids.append(x.strip())
    return ids

#Returns a list of ONLY all of the song ids from the playlist
def get_song_ids(ids):  
    username=(ids[1])
    index=0
    tracks=[]
    for elm in ids:
        if username in elm:
            tracks.append(ids[index-1])
        index+=1
    tracks.append(ids[-1])
    tracks=tracks[2:]
    return tracks

#Gets rid of '"id:"', so we only have the actual id
def ids_to_features(tracks):
    songIDs=[]
    for song in tracks:
        key, value = map(str.strip, song.split(':'))
        songIDs.append(value.strip('"'))
    return songIDs

def extract_values(list_of_dict):
    # Use a list comprehension to get only the values
    final=[]
    for dicts in list_of_dict:
        values_list = [value for value in dicts.values()]
        final.append(values_list)

    return final

def explicit_check(ordered_list):
    explicit_bools = []
    for lists in ordered_list:
        for dicts in lists:
            bools = dicts.get("explicit")
            explicit_bools.append(bools)
            
    
    falseCount = 0
    trueCount = 0
    explicit_or_no = 0

    for bools in explicit_bools:
        if (bools==False):
            falseCount+=1
        elif (bools==True):
            trueCount+=1

    if falseCount>trueCount:
        explicit_or_no=0
        return explicit_or_no
    else:
        explicit_or_no=1
        return explicit_or_no

#Calculates and returns the mean of values for a given category of a given playlist
def mean_calculator(playlist, category):
    mean=0
    total=0
    amount=len(playlist)
    for i in range(amount):
        total+=playlist[i][category]
        mean=total/amount
    return mean

def out_of_one(categ1, categ2):
    dif = abs(categ1-categ2)
    if(0.50<dif<=0.80):
        outta_one = (1-dif*1.25)
    if (dif<=0.50):
        outta_one = (1-dif*2)
    else:
        outta_one = (1-dif)
    return outta_one

def out_of_sixty(dcb1, dcb2):
    abs_dcb1 = abs(dcb1)
    abs_dcb2 = abs(dcb2)
    dif = abs(abs_dcb1-abs_dcb2)
    outta_sixty=(60-dif)

    if (outta_sixty < 30):
        return 0
    if (30 <= outta_sixty < 40):
        return 0.10
    if (40 <= outta_sixty<45):
        return 0.20
    if (45 <= outta_sixty<50):
        return 0.50
    if(50 <= outta_sixty<52):
        return 0.60
    if (52 <= outta_sixty< 54):
        return 0.70
    if (54 <= outta_sixty<56):
        return 0.80
    if (56 <= outta_sixty<58):
        return 0.90
    if (58 <= outta_sixty):
        return 1.0
    
    




def main():
    #Spotify authentication
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    #User input for playlist URLs
    url_pl_id_one=input("Provide a URL for the first playlist here:")
    url_pl_id_two=input("Provide a URL for the second playlist here:")

    #Using Spotpipy module to get playlist info
    results1 = sp.playlist(url_pl_id_one)
    playlist1 = (json.dumps(results1, indent=4))
    results2 = sp.playlist(url_pl_id_two)
    playlist2 = (json.dumps(results2, indent=4)) 

    playlist1_ids=idlist(playlist1)
    playlist2_ids=idlist(playlist2)
    playlist1_song_ids=get_song_ids(playlist1_ids)
    playlist2_song_ids=get_song_ids(playlist2_ids)
    playlist1_final=ids_to_features(playlist1_song_ids)
    playlist2_final=ids_to_features(playlist2_song_ids)

    
    playlist1_trackinfo=sp.tracks(playlist1_final) 
    explicit1=explicit_check((list(playlist1_trackinfo.values())))
    
    playlist2_trackinfo=sp.tracks(playlist2_final)
    explicit2=explicit_check((list(playlist2_trackinfo.values())))
    
    playlist1_features=sp.audio_features(playlist1_final)
    playlist2_features=sp.audio_features(playlist2_final)
    outsource1=(extract_values(playlist1_features))
    outsource2=(extract_values(playlist2_features))
   
    energy1=mean_calculator(outsource1, 1)
    energy2=mean_calculator(outsource2, 1)
    loudness1=mean_calculator(outsource1, 3)
    loudness2=mean_calculator(outsource2, 3)
    acous1=mean_calculator(outsource1, 6)
    acous2=mean_calculator(outsource2, 6)
    instru1=mean_calculator(outsource1, 7)
    instru2=mean_calculator(outsource2, 7)
    valence1=mean_calculator(outsource1, 9)
    valence2=mean_calculator(outsource2, 9)

    Fenergy = out_of_one(energy1, energy2)
    
    Facousticness = out_of_one(acous1, acous2)
    
    Finstrumentalness = out_of_one(instru1, instru2)
    
    Fvalence = out_of_one(valence1, valence2)
    
    Floudness = out_of_sixty(loudness1, loudness2)
    

    Fexplicit=0
    if (abs(explicit1-explicit2)==0):
        Fexplicit=1.0
    elif (abs(explicit1-explicit2)==1):
        Fexplicit=0
    

    final = 3*Fenergy+3*Facousticness+(0.1)*Finstrumentalness+(0.5)*Fvalence+(0.1)*Floudness+2*Fexplicit
    return((final/8.7)*100)


if __name__ == '__main__':
     main()




        





        








