from solid_components import SolidComponents
import pandas as pd
import numpy as np


class Jacket(SolidComponents):

    # Class for jacket objects

    ### INPUT PARAMETERS
    # some are inherited from class SolidComponents

    ### THERMOPHYSICAL PROPERTIES
    # inherited from class SolidComponents

    ### OPERATIONAL PARAMETERS
    # inherited from class SolidComponents

    ### COMPUTED IN INITIALIZATION
    # inherited from class SolidComponents

    ### COMPUTED VECTOR FOR MAGNETIC FIELD
    # inherited from class SolidComponents

    KIND = "Jacket"

    def __init__(self, simulation, sheet, icomp, name, dict_file_path):

        self.NAME = name
        # get channels ID consistently with user definition (cdp, 09/2020)
        self.ID = sheet.cell(row=3, column=4 + icomp).value

        # dictionary declaration (cdp, 11/2020)
        self.dict_input = dict()
        self.dict_operation = dict()
        self.dict_node_pt = dict()
        self.dict_Gauss_pt = dict()
        self.dict_num_step = dict()
        self.radiative_heat_env = ""
        self.radiative_heat_inn = dict()
        # Empty dictionary of list to save variable time evolutions at selected spatial coordinates.
        self.time_evol = dict(temperature=dict())
        # Dictionary initialization: dict_input.
        self.dict_input = pd.read_excel(
            dict_file_path["input"],
            sheet_name=sheet.title,
            skiprows=2,
            header=0,
            index_col=0,
            usecols=["Variable name", self.ID],
        )[self.ID].to_dict()
        # Dictionary initialization: dict_operation.
        self.dict_operation = pd.read_excel(
            dict_file_path["operation"],
            sheet_name=sheet.title,
            skiprows=2,
            header=0,
            index_col=0,
            usecols=["Variable name", self.ID],
        )[self.ID].to_dict()

        if self.dict_operation["IBIFUN"] != -1:
            # Remove key B_field_units.
            del self.dict_operation["B_field_units"]

        # Call SolidComponents class constructor to deal with Jacket time \
        # steps for current, external heating and so on (cdp, 11/2020)
        SolidComponents(simulation, self)

    def __repr__(self):
        return f"{self.__class__.__name__}(Type: {self.NAME}, ID: {self.ID})"

    def __str__(self):
        pass

    def _radiative_source_therm_env(self, conductor, environment):
        """Method that evaluates the heat transferred by radiation with the external environment.

        Args:
            conductor ([type]): [description]
            environment ([type]): [description]
        """
        key = f"{environment.KIND}_{self.ID}"
        if (
            conductor.dict_input["METHOD"] == "BE"
            or conductor.dict_input["METHOD"] == "CN"
        ):
            # Backward Euler or Crank-Nicolson.
            if conductor.cond_time[-1] == 0:
                # Initialization.
                self.radiative_heat_env = np.zeros(
                    (conductor.dict_discretization["N_nod"], 2)
                )
            elif conductor.cond_time[-1] > 0:
                if conductor.cond_num_step == 1:
                    # Store the old values only immediately after the initializzation, \
                    # since after that the whole SYSLOD array is saved and there is no \
                    # need to compute twice the same values.
                    self.radiative_heat_env[:, 1] = self.radiative_heat_env[:, 0].copy()
                # Update value at the current time step.
                self.radiative_heat_env[:, 0] = (
                    conductor.dict_interf_peri["env_sol"][key]
                    * conductor.dict_node_pt["HTC"]["env_sol"][key]["rad"]
                    * (
                        environment.dict_input["Temperature"]
                        - self.dict_node_pt["temperature"]
                    )
                )
            # end if conductor.cond_time[-1].
        elif conductor.dict_input["METHOD"] == "AM4":
            # Adams-Moulton 4.
            if conductor.cond_time[-1] == 0:
                # Initialization.
                self.radiative_heat_env = np.zeros(
                    (conductor.dict_discretization["N_nod"], 4)
                )
            elif conductor.cond_time[-1] > 0:
                self.radiative_heat_env[:, 1:4] = self.radiative_heat_env[:, 0:3].copy()
                # Update value at the current time step.
                self.radiative_heat_env[:, 0] = (
                    conductor.dict_interf_peri["env_sol"][key]
                    * conductor.dict_node_pt["HTC"]["env_sol"][key]["rad"]
                    * (
                        environment.dict_input["Temperature"]
                        - self.dict_node_pt["temperature"]
                    )
                )
            # end if conductor.cond_time[-1].
        # end if conductor.dict_input["METHOD"].

    # End method _radiative_source_therm.

    def _radiative_heat_exc_inner(self, conductor, jk_inner):
        """Method that evaluates the heat transferred by radiation with the inner surface of the enclosure and the inner jackets.

        Args:
            conductor ([type]): [description]
            environment ([type]): [description]
        """
        if self.ID < jk_inner.ID:
            key = f"{self.ID}_{jk_inner.ID}"
        else:
            key = f"{jk_inner.ID}_{self.ID}"
        # End if self.ID.
        if (
            conductor.dict_input["METHOD"] == "BE"
            or conductor.dict_input["METHOD"] == "CN"
        ):
            # Backward Euler or Crank-Nicolson.
            if conductor.cond_time[-1] == 0:
                # Initialization.
                self.radiative_heat_inn[key] = np.zeros(
                    (conductor.dict_discretization["N_nod"], 2)
                )
            elif conductor.cond_time[-1] > 0:
                if conductor.cond_num_step == 1:
                    # Store the old values only immediately after the initializzation, \
                    # since after that the whole SYSLOD array is saved and there is no \
                    # need to compute twice the same values.
                    self.radiative_heat_inn[key][:, 1] = self.radiative_heat_inn[key][
                        :, 0
                    ].copy()
                # Update value at the current time step.
                self.radiative_heat_inn[key][:, 0] = (
                    conductor.dict_interf_peri["sol_sol"][key]
                    * conductor.dict_node_pt["HTC"]["sol_sol"][key]["rad"]
                    * (
                        jk_inner.dict_node_pt["temperature"]
                        - self.dict_node_pt["temperature"]
                    )
                )
            # end if conductor.cond_time[-1].
        elif conductor.dict_input["METHOD"] == "AM4":
            # Adams-Moulton 4.
            if conductor.cond_time[-1] == 0:
                # Initialization.
                self.radiative_heat_inn[key] = np.zeros(
                    (conductor.dict_discretization["N_nod"], 4)
                )
            elif conductor.cond_time[-1] > 0:
                self.radiative_heat_inn[key][:, 1:4] = self.radiative_heat_inn[key][
                    :, 0:3
                ].copy()
                # Update value at the current time step.
                self.radiative_heat_inn[key][:, 0] = (
                    conductor.dict_interf_peri["sol_sol"][key]
                    * conductor.dict_node_pt["HTC"]["sol_sol"][key]["rad"]
                    * (
                        jk_inner.dict_node_pt["temperature"]
                        - self.dict_node_pt["temperature"]
                    )
                )
            # end if conductor.cond_time[-1].
        # end if conductor.dict_input["METHOD"].

    # End method _radiative_source_therm.

    # agiungere metodi per calcolo proprietà nel gauss point
