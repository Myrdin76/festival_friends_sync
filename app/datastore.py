from app.models import Artist


class ArtistStore():
    def __init__(self, festival):
        self.festival = festival
        self.stages = None
        self.artists = None
        self.days = None
    
    def get_stages(self):
        if self.stages is None:
            try:
                rows = Artist.query.filter_by(festival=self.festival).distinct(Artist.stage).distinct()
                self.stages = [row.stage for row in rows]
                return self.stages
            except:
                return []
        else:
            return self.stages
            
    def get_artists(self):
        if self.artists is None:
            try:
                rows = Artist.query.filter_by(festival=self.festival).distinct(Artist.name).distinct()
                self.artists = [row.name for row in rows]
                return self.artists
            except:
                return []
        else:
            return self.artists
    
    def get_days(self):
        if self.days is None:
            try:
                rows = Artist.query.filter_by(festival=self.festival).distinct(Artist.day).distinct()
                self.days = [row.day for row in rows]
                return self.days
            except:
                return []
        else:
            return self.days