from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from .base import Base

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    versions = relationship(
        "RecipeVersion",
        back_populates="recipe",
        order_by="RecipeVersion.version",
    )

    @property
    def latest_version_id(self):
        return self.versions[-1].id if self.versions else None


class RecipeVersion(Base):
    __tablename__ = "recipe_versions"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    version = Column(Integer, default=1)
    ingredients = Column(JSON)
    hydration_percentage = Column(Float)
    spawn_ratio = Column(Float)
    notes = Column(String)

    recipe = relationship("Recipe", back_populates="versions")