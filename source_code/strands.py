from solid_components import SolidComponents
from openpyxl import load_workbook
import numpy as np
import os
from UtilityFunctions.auxiliary_functions import get_from_xlsx

# from UtilityFunctions.InitializationFunctions import Read_input_file
# NbTi properties
from Properties_of_materials.niobium_titanium import (
    critical_temperature_nbti,
    critical_current_density_nbti,
    current_sharing_temperature_nbti,
)

# Nb3Sn properties
from Properties_of_materials.niobium3_tin import (
    critical_temperature_nb3sn,
    critical_current_density_nb3sn,
    current_sharing_temperature_nb3sn,
)

# RE123 properties
from Properties_of_materials.rare_earth_123 import (
    critical_magnetic_field_re123,
    critical_current_density_re123,
    current_sharing_temperature_re123,
)


class Strands(SolidComponents):

    ### INPUT PARAMETERS

    ### OPERATIONAL PARAMETERS
    # inherited from class SolidComponents

    ### COMPUTED IN INITIALIZATION
    # inherited from class SolidComponents

    KIND = "Strand"

    def get_magnetic_field_gradient(self, conductor, nodal=True):

        """
        ############################################################################
        #              Get_alphaB(self, comp)
        ############################################################################
        #
        # Method that initialize magnetic field gradient in python objects of class
        # Strands.
        #
        ############################################################################
        # VARIABLE              I/O    TYPE              DESCRIPTION            UNIT
        # --------------------------------------------------------------------------
        # comp                  I      object            python object of
        #                                                class Strands             -
        # xcoord*               I      np array float    conductor spatial
        #                                                discretization            m
        # IOPFUN*               I      scalar integer    flag to decide how to
        #                                                evaluate current:
        #                                                == 0 -> constant;
        #                                                == 1 -> exponential decay;
        #                                                == -1 -> read from
        #                                                I_file_dummy.xlsx         -
        # IOP_TOT*              I      scalar float      total operation
        #                                                current                   A
        # IOP0_TOT*             I      scalar float      total operation current
        #                                                @ time = 0                A
        # IALPHAB§              I      scalar integer    flag to define the
        #                                                magnetic field gradient
        #                                                along the strand:
        #                                                == 0 -> no gradient;
        #                                                == -1 -> read from
        #                                                alphab.xlsx               -
        # BASE_PATH*             I      string           path of folder Description
        #                                               of Components              -
        # External_current_path* I     string           name of the external
        #                                               file from which
        #                                               interpolate magnetic
        #                                               field gradient value       -
        # alphaB§               O      np array float   magnetic field
        #                                               gradient                 T/m
        #############################################################################
        # Invoched functions/methods: Get_from_xlsx
        #
        ############################################################################
        # * xcoord, IOPFUN, IOP_TOT, IOP0_TOT, BASE_PATH and External_current_path
        # are given by conductor.xcoord, conductor.dict_input["IOPFUN"], conductor.IOP_TOT, conductor.dict_input["IOP0_TOT"],
        # conductor.BASE_PATH and conductor.file_input["EXTERNAL_CURRENT"].
        # § IALPHAB and alphaB are component attributes: self.IALPHAB, self.dict_node_pt["alpha_B"].
        # N.B. alphaB is a Strands attribute so its value can be assigned
        # directly, it has the same of shape of xcoord and it is a np array.
        ############################################################################
        #
        # Translated and optimized by D. Placido Polito 06/2020
        #
        ############################################################################
        """

        if nodal:
            # compute alpha_B in each node (cdp, 07/2020)
            if self.dict_operation["IALPHAB"] <= -1:  # read from file
                # call Get_from_xlsx on the component
                path = os.path.join(
                    conductor.BASE_PATH, conductor.file_input["EXTERNAL_ALPHAB"]
                )
                # leggi un file come del campo magnetico
                # controlla se e' per unita' di corrente
                # in caso affermatico moltiplica per IOP_TOT
                [self.dict_node_pt["alpha_B"], flagSpecfield] = get_from_xlsx(
                    conductor, path, self, "IALPHAB"
                )
                if flagSpecfield == 2:  # alphaB is per unit of current
                    self.dict_node_pt["alpha_B"] = (
                        self.dict_node_pt["alpha_B"] * conductor.IOP_TOT
                    )
                if conductor.dict_input["IOPFUN"] < 0:
                    self.dict_node_pt["alpha_B"] = (
                        self.dict_node_pt["alpha_B"]
                        * conductor.IOP_TOT
                        / conductor.dict_input["IOP0_TOT"]
                    )
            elif self.dict_operation["IALPHAB"] == 0:
                self.dict_node_pt["alpha_B"] = np.zeros(
                    conductor.dict_discretization["N_nod"]
                )
        elif nodal == False:
            # compute alpha_B in each Gauss point (cdp, 07/2020)
            self.dict_Gauss_pt["alpha_B"] = (
                np.abs(
                    self.dict_node_pt["alpha_B"][
                        0 : conductor.dict_discretization["N_nod"] - 1
                    ]
                    + self.dict_node_pt["alpha_B"][
                        1 : conductor.dict_discretization["N_nod"] + 1
                    ]
                )
                / 2.0
            )

    def get_superconductor_critical_prop(self, conductor, nodal=True):

        """
        Calcola i margini
        usa temperatura strand
        Usa campo magnetico BFIELD
        usa EPSI
        usa alphaB
        :return: Jcritck Tcritchk TCSHRE TCSHREmin
        """

        # Properties evaluation in each nodal point (cdp, 07/2020)
        # Variable where is necessary to correctly evaluate EPSILON calling method \
        # Get_EPS (cdp, 07/2020)
        if nodal:
            self.dict_node_pt = self.eval_critical_properties(self.dict_node_pt)
        # Properties evaluation in each Gauss point (cdp, 07/2020)
        elif nodal == False:
            self.dict_Gauss_pt = self.eval_critical_properties(self.dict_Gauss_pt)

    # End of Method get_superconductor_critical_prop

    def eval_critical_properties(self, dict_dummy):

        self.JOP = np.abs(self.dict_node_pt["IOP"][0]) / (
            self.ASC * self.dict_input["COSTETA"]
        )

        # bmax moved here since it is not dependent on flag ISUPERCONDUCTOR \
        # (cdp, 07/2020)
        bmax = dict_dummy["B_field"] * (1 + dict_dummy["alpha_B"])
        if self.dict_input["ISUPERCONDUCTOR"] == "NbTi":
            dict_dummy["T_critical"] = critical_temperature_nbti(
                dict_dummy["B_field"], self.dict_input["Tc0m"], self.dict_input["Bc20m"]
            )
            dict_dummy["J_critical"] = critical_current_density_nbti(
                dict_dummy["temperature"],
                dict_dummy["B_field"],
                self.dict_input["Tc0m"],
                self.dict_input["Bc20m"],
                self.dict_input["c0"],
            )
            dict_dummy["T_cur_sharing"] = current_sharing_temperature_nbti(
                dict_dummy["B_field"],
                self.JOP,
                self.dict_input["Tc0m"],
                self.dict_input["Bc20m"],
                self.dict_input["c0"],
            )
            dict_dummy["T_cur_sharing_min"] = current_sharing_temperature_nbti(
                bmax,
                self.JOP,
                self.dict_input["Tc0m"],
                self.dict_input["Bc20m"],
                self.dict_input["c0"],
            )
        elif self.dict_input["ISUPERCONDUCTOR"] == "Nb3Sn":
            dict_dummy["T_critical"] = critical_temperature_nb3sn(
                dict_dummy["B_field"],
                dict_dummy["Epsilon"],
                self.dict_input["Tc0m"],
                self.dict_input["Bc20m"],
            )
            dict_dummy["J_critical"] = critical_current_density_nb3sn(
                dict_dummy["temperature"],
                dict_dummy["B_field"],
                dict_dummy["Epsilon"],
                self.dict_input["Tc0m"],
                self.dict_input["Bc20m"],
                self.dict_input["c0"],
            )
            dict_dummy["T_cur_sharing"] = current_sharing_temperature_nb3sn(
                dict_dummy["B_field"],
                dict_dummy["Epsilon"],
                self.JOP,
                self.dict_input["Tc0m"],
                self.dict_input["Bc20m"],
                self.dict_input["c0"],
            )
            dict_dummy["T_cur_sharing_min"] = current_sharing_temperature_nb3sn(
                bmax,
                dict_dummy["Epsilon"],
                self.JOP,
                self.dict_input["Tc0m"],
                self.dict_input["Bc20m"],
                self.dict_input["c0"],
            )
        elif self.dict_input["ISUPERCONDUCTOR"] == "HTS":
            dict_dummy["T_critical"] = self.dict_input["Tc0m"] * np.ones(
                dict_dummy["temperature"].shape
            )
            dict_dummy["J_critical"] = critical_current_density_re123(
                dict_dummy["temperature"],
                dict_dummy["B_field"],
                self.dict_input["Tc0m"],
                self.dict_input["Bc20m"],
                self.dict_input["c0"],
            )
            dict_dummy["T_cur_sharing"] = current_sharing_temperature_re123(
                dict_dummy["B_field"],
                self.JOP,
                self.dict_input["Tc0m"],
                self.dict_input["Bc20m"],
                self.dict_input["c0"],
            )
            dict_dummy["T_cur_sharing_min"] = current_sharing_temperature_re123(
                bmax,
                self.JOP,
                self.dict_input["Tc0m"],
                self.dict_input["Bc20m"],
                self.dict_input["c0"],
            )
        elif self.dict_input["ISUPERCONDUCTOR"] == "scaling.dat":
            # Get user defined scaling invoking method User_scaling_margin \
            # (cdp, 10/2020)
            self.user_scaling_margin()

        return dict_dummy

    # end method Eval_critical_properties (cdp, 10/2020)

    def get_eps(self, conductor, nodal=True):
        # For each strand of type MixSCStabilizer or SuperConductor (cdp, 06/2020)
        if nodal:
            # compute Epsilon in each node (cdp, 07/2020)
            if self.dict_operation["IEPS"] < 0:  # strain from file strain.dat
                path = os.path.join(
                    conductor.BASE_PATH, conductor.file_input["EXTERNAL_STRAIN"]
                )
                # call Get_from_xlsx on the component
                [self.dict_node_pt["Epsilon"], flagSpecfield] = get_from_xlsx(
                    conductor, path, self, "IEPS"
                )
                if flagSpecfield == 1:
                    print("still to be decided what to do here\n")
            elif self.dict_operation["IEPS"] == 0:  # no strain (cdp, 06/2020)
                self.dict_node_pt["Epsilon"] = np.zeros(
                    conductor.dict_discretization["N_nod"]
                )
            elif self.dict_operation["IEPS"] == 1:
                # constant strain to the value in input file \
                # conductor_i_operation.xlsx (cdp, 06/2020)
                self.dict_node_pt["Epsilon"] = self.dict_operation["EPS"] * np.ones(
                    conductor.dict_discretization["N_nod"]
                )
        elif nodal == False:
            # compute Epsilon in each Gauss point (cdp, 07/2020)
            self.dict_Gauss_pt["Epsilon"] = (
                self.dict_node_pt["Epsilon"][
                    0 : conductor.dict_discretization["N_nod"] - 1
                ]
                + self.dict_node_pt["Epsilon"][
                    1 : conductor.dict_discretization["N_nod"] + 1
                ]
            ) / 2.0

    # end method Get_EPS (cdp, 10/2020)

    def user_scaling_margin(self):

        """
        Method that read file scaling_input.dat to get the user scaling for SuperConductors strands and convert it into an attribute dictionary (cdp, 10/2020)
        """

        # declare dictionary (cdp, 10/2020)
        # construct list of integer values (cdp, 10/2020)
        list_integer = ["emode", "ieavside"]
        # Loop to read file scaling_input.dat by lines and construct a \
        # dictionary (cdp, 10/2020)
        with open("scaling_input.dat", "r") as scaling:
            # Read lines (cdp, 10/2020)
            for line in scaling:
                if line[0] == "#" or line[0] == "\n":
                    # escape comments and void lines (cdp, 10/2020)
                    pass
                else:
                    # split the list into two fields, fields[0] is dictionary key,
                    # fields[1] is the corresponding value. The final \n is ignored \
                    # considering only the first [:-1] characters in string fields[1] \
                    # (cdp, 10/2020)
                    fields = line.split(" = ")
                    if fields[0] in list_integer:
                        # convert to integer (cdp, 10/2020)
                        self.dict_scaling_input[fields[0]] = int(fields[1][:-1])
                    elif fields[0] == "ISUPERCONDUCTOR":
                        # flag to
                        self.dict_scaling_input[fields[0]] = str(fields[1][:-1])
                    else:
                        # convert to float (cdp, 10/2020)
                        self.dict_scaling_input[fields[0]] = float(fields[1][:-1])
                    # end if fields[0] (cdp, 10/2020)
                # end if line[0] (cdp, 10/2020)
            # end for line (cdp, 10/2020)
        # end with (cdp, 10/2020)

    # end method User_scaling_margin (cdp, 10/2020)
