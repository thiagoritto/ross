"""Materials module.

This module defines the Material class and defines
some of the most common materials used in rotors.
"""
import os
import numpy as np
import toml
import ross as rs

from pathlib import Path
__all__ = ["Material", "steel"]


class Material:
    """Material used on shaft and disks.

    Class used to create a material and define its properties.
    Density and at least 2 arguments from E, G_s and Poisson should be
    provided.

    You can run rs.Material.available_materials() to get a list of materials
    already provided.

    Parameters
    ----------
    name : str
        Material name.
    E : float
        Young's modulus (N/m**2).
    G_s : float
        Shear modulus (N/m**2).
    rho : float
        Density (N/m**3).
    color : str
        Can be used on plots.

    Examples
    --------
    >>> AISI4140 = Material(name='AISI4140', rho=7850, E=203.2e9, G_s=80e9)
    >>> Steel = Material(name="Steel", rho=7810, E=211e9, G_s=81.2e9)
    >>> AISI4140.Poisson
    0.27

    """

    def __init__(self, name, rho, **kwargs):

        assert name is not None, "Name not provided"
        assert type(name) is str, "Name must be a string"
        assert " " not in name, "Spaces are not allowed in Material name"
        assert (
            sum([1 if i in ["E", "G_s", "Poisson"] else 0 for i in kwargs]) > 1
        ), "At least 2 arguments from E, G_s and Poisson should be provided"

        self._name = name
        self.rho = rho
        self.E = kwargs.get("E", None)
        self.Poisson = kwargs.get("Poisson", None)
        self.G_s = kwargs.get("G_s", None)
        self.color = kwargs.get("color", "#525252")

        if self.E is None:
            self.E = self.G_s * (2 * (1 + self.Poisson))
        elif self.G_s is None:
            self.G_s = self.E / (2 * (1 + self.Poisson))
        elif self.Poisson is None:
            self.Poisson = (self.E / (2 * self.G_s)) - 1

    def __eq__(self, other):
        """Material is considered equal if properties are equal."""
        self_list = [v for v in self.__dict__.values() if isinstance(v, (float, int))]
        other_list = [v for v in self.__dict__.values() if isinstance(v, (float, int))]

        if np.allclose(self_list, other_list):
            return True
        else:
            return False

    def __repr__(self):
        selfE = "{:.3e}".format(self.E)
        selfPoisson = "{:.3e}".format(self.Poisson)
        selfrho = "{:.3e}".format(self.rho)
        selfGs = "{:.3e}".format(self.G_s)

        return (
            f"Material"
            f'(name="{self.name}", rho={selfrho}, G_s={selfGs}, '
            f"E={selfE}, Poisson={selfPoisson}, color={self.color!r})"
        )

    def __str__(self):
        return (
            f"{self.name}"
            f'\n{35*"-"}'
            f"\nDensity         (N/m**3): {float(self.rho):{2}.{8}}"
            f"\nYoung`s modulus (N/m**2): {float(self.E):{2}.{8}}"
            f"\nShear modulus   (N/m**2): {float(self.G_s):{2}.{8}}"
            f"\nPoisson coefficient     : {float(self.Poisson):{2}.{8}}"
        )

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        try:
            self._name = str(name)
        except:
            "Material's name must be a string."

    @staticmethod
    def dump_data(data, path=os.path.dirname(rs.__file__)):
        with open(Path(path)/"available_materials.toml", "w") as f:
            toml.dump(data, f)

    @staticmethod
    def load_data(path=os.path.dirname(rs.__file__)):
        try:
            with open(Path(path)/"available_materials.toml", "r") as f:
                data = toml.load(f)
        except FileNotFoundError:
            data = {"Materials": {}}
            Material.dump_data(data, path)
        return data

    @staticmethod
    def use_material(name, path=os.path.dirname(rs.__file__)):
        data = Material.load_data(path)
        try:
            material = data["Materials"][name]
            return Material(**material)
        except KeyError:
            raise KeyError("There isn't a instanced material with this name.")

    @staticmethod
    def remove_material(name, path=os.path.dirname(rs.__file__)):
        data = Material.load_data(os.path.dirname(rs.__file__))
        try:
            del data["Materials"][name]
        except KeyError:
            return "There isn't a saved material with this name."
        Material.dump_data(data)

    @staticmethod
    def available_materials(path=os.path.dirname(rs.__file__)):
        try:
            data = Material.load_data(path)
            return list(data["Materials"].keys())
        except FileNotFoundError:
            return "There is no saved materials."

    def save_material(self, path=os.path.dirname(rs.__file__)):
        data = Material.load_data(path)
        material_dict = self.__dict__.copy()
        material_dict['name'] = material_dict.pop('_name')
        data["Materials"][self.name] = material_dict

        Material.dump_data(data, path)


steel = Material(name="Steel", rho=7810, E=211e9, G_s=81.2e9)
