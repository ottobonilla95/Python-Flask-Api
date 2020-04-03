from cloudinary.uploader import upload
from cloudinary import config

# class in charge of upload images
class CloudinaryHandler:
    @classmethod
    def LoadImage (cls, base64):
        config( 
            cloud_name = "de1xlc3s1", 
            api_key = "962536298833484", 
            api_secret = "DxjiGuYYI51ID6x8IpwkFpx2QFY" 
            )
        
        result= upload(base64)
        return result["url"];