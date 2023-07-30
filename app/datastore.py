from app.models import Artist


class ArtistStore():
    def __init__(self, festival):
        self.festival = festival
        self.stages = self.get_stages()
        self.artists = self.get_artists()
        self.days = self.get_days()
        
    def data(self):
        return self.data
    
    def get_stages(self):
        try:
            rows = Artist.query.filter_by(festival=self.festival).distinct(Artist.stage).distinct()
            return [row.stage for row in rows]
        except:
            return []
            
    def get_artists(self):
        try:
            rows = Artist.query.filter_by(festival=self.festival).distinct(Artist.name).distinct()
            return [row.name for row in rows]
        except:
            return []
    
    def get_days(self):
        try:
            rows = Artist.query.filter_by(festival=self.festival).distinct(Artist.day).distinct()
            return [row.day for row in rows]
        except:
            return []