from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "Plant Disease Detection CV Service"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8001
    MODEL_PATH: str = "models/plant_disease_resnet.pth"
    IMAGE_SIZE: int = 224
    NUM_CLASSES: int = 38          # PlantVillage has 38 classes

    class Config:
        env_file = ".env"


settings = Settings()
