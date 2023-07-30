from app.datastore import ArtistStore

def test_datastore(client_all_access):
    with client_all_access:
        asd = ArtistStore("Lowlands")
        asd.get_stages()
        asd.get_artists()
        print(asd.stages)
        print(asd.artists)