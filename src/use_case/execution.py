from os import environ
from typing import Union
from uuid import UUID

from abmodel import (
    EvolutionModes,
    ExecutionModes,
    Population
)

from src.services import CloudAPI
from src.use_case.files import UploadBucketFile
from src.use_case.groups import (
    ValidateDiseaseGroup,
    ValidateMRGroup,
    ValidateNaturalHistoryGroup,
    ValidateQuarantineGroups,
    ValidateSimpleGroup,
    ValidateSusceptibilityGroup,
    ValidateIsolationAdherenceGroups,
    ValidateImmunizationGroups,
    ValidateMobilityGroups,
    ValidateMRTPolicies,
    ValidateinitialPopulationSetupList,
    ValidateConfiguration,
    ValidateHealthSystem,
    ValidateGlobalCyclicMR,
    ValidateCyclicMRPolicies
)


class StartExecution:

    @classmethod
    def handle(cls, data: dict):
        simulation_uuid = data.get("configuration").get("identifier")
        try:
            print("Procesando")
            configuration = ValidateConfiguration.handle(
                data.get("configuration"))

            health_system = ValidateHealthSystem.handle(
                data.get("health_system"))

            age_groups = ValidateSimpleGroup.handle(data.get("age_groups"))

            mr_groups = ValidateMRGroup.handle(data.get("mr_groups"))

            vulnerability_groups = ValidateSimpleGroup.handle(
                data.get("vulnerability_groups")
            )

            susceptibility_groups = ValidateSusceptibilityGroup.handle(
                data.get("susceptibility_groups")
            )

            isolation_adherence_groups = ValidateIsolationAdherenceGroups.handle(
                data.get("isolation_adherence_groups")
            )

            immunization_groups = ValidateImmunizationGroups.handle(
                data.get("immunization_groups")
            )

            mobility_groups = ValidateMobilityGroups.handle(
                data.get("mobility_groups")
            )

            disease_groups = ValidateDiseaseGroup.handle(
                data.get("disease_groups"))

            natural_history = ValidateNaturalHistoryGroup.handle(
                data.get("natural_history")
            )

            mrt_policies = ValidateMRTPolicies.handle(data.get("mrt_policies"))

            initial_population_setup_list = data.get(
                "initial_population_setup_list")

            global_cyclic_mr = ValidateGlobalCyclicMR.handle(
                data.get("global_cyclic_mr"))

            cyclic_mr_policies = ValidateCyclicMRPolicies.handle(
                data.get("cyclic_mr_policies"))

            population = Population(
                configuration=configuration,
                health_system=health_system,
                age_groups=age_groups,
                vulnerability_groups=vulnerability_groups,
                mr_groups=mr_groups,
                susceptibility_groups=susceptibility_groups,
                mobility_groups=mobility_groups,
                disease_groups=disease_groups,
                natural_history=natural_history,
                initial_population_setup_list=initial_population_setup_list,
                mrt_policies=mrt_policies,
                global_cyclic_mr=global_cyclic_mr,
                cyclic_mr_policies=cyclic_mr_policies,
                immunization_groups=immunization_groups,
                isolation_adherence_groups=isolation_adherence_groups,
                execmode=ExecutionModes.iterative.value,
                evolmode=EvolutionModes.steps.value
            )

            filepaths_dict = {}
            for step in range(100):
                population.evolve(iterations=1)
                df = population.get_population_df()
                filepaths_dict[step] = f"path_{step}"

            UploadBucketFile.handle(simulation_uuid, b'testing')

            FinishEmergencyExecution.handle(simulation_uuid)
        except Exception as error:
            print(error)
            FinishEmergencyExecution.handle(simulation_uuid, emergency=True)


class FinishEmergencyExecution:

    @ classmethod
    def handle(
        cls,
        simulation_uuid: Union[UUID, str],
        emergency: bool = False
    ):
        data = cls._get_machine_information()
        response, is_invalid = CloudAPI.finish_simulation(
            str(simulation_uuid),
            data=data,
            emergency=emergency
        )
        if is_invalid:
            raise RuntimeError("Can not stop execution in machine")

    @ classmethod
    def _get_machine_information(cls) -> dict:
        for k, v in environ.items():
            print(f"{k}: {v}")
        return {
            'name': environ.get("HOSTNAME", "unknown"),
        }
