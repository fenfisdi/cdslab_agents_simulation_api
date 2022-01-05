from datetime import datetime
from typing import List
from uuid import uuid1

from abmodel.models.base import SimpleGroups
from abmodel.models.disease import (
    DiseaseStates,
    NaturalHistory,
    SusceptibilityGroups,
    IsolationAdherenceGroups,
    ImmunizationGroups,
    MobilityGroups
)
from abmodel.models import (
    MRTracingPolicies,
    Configutarion,
    BoxSize,
    HealthSystem
)

from abmodel.models.mobility_restrictions import CyclicMRPolicies, GlobalCyclicMR


class ValidateSimpleGroup:

    @classmethod
    def handle(cls, data: List[dict]) -> SimpleGroups:
        return SimpleGroups(names=[group["name"] for group in data])

class ValidateSusceptibilityGroup:

    @classmethod
    def handle(cls, data: List[dict]) -> SusceptibilityGroups:
        dist_title = "susceptibility_dist"
        group_info = []
        for group in data:
            distribution_data = group.get("distribution")
            new_distribution = {
                "dist_title": dist_title,
                "dist_type": distribution_data.get("type", "weights"),
                "dist_name": f"{group.get('name')}_{uuid1().hex}",
            }

            # Update kwargs for each distribution
            kwargs = distribution_data.get("kwargs", {})
            if distribution_data.get("type") == "constant":
                new_distribution["constant"] = kwargs.get("constant")
            if distribution_data.get("type") == "numpy":
                new_distribution["kwargs"] = kwargs
                new_distribution["dist_type"] = distribution_data.get(
                    "numpy_type"
                )
            else:
                new_distribution["kwargs"] = kwargs

            group_info.append(
                {
                    "name": group.get("name"),
                    "dist_info": new_distribution,
                }
            )

        return SusceptibilityGroups(
            dist_title=dist_title,
            group_info=group_info
        )

class ValidateDiseaseGroup:

    @classmethod
    def handle(cls, data: List[dict]) -> DiseaseStates:
        distribution_dict = {
            "diagnosis": "diagnosis_prob",
            "isolation": "isolation_days",
            "hospitalization": "hospitalization_prob",
            "icu": "ICU_prob",
        }

        group_info = []
        for group in data:
            distribution_data = group.get("distributions")

            distribution_information = []
            for distribution, values in distribution_data.items():
                new_distribution = {
                    "dist_title": distribution_dict.get(distribution),
                    "dist_type": values.get("type"),
                    "dist_name": f"{group.get('name')}_{uuid1().hex}",
                }

                kwargs = distribution_data.get("kwargs", {})
                if distribution_data.get("type") == "constant":
                    new_distribution["constant"] = kwargs.get("constant")
                if distribution_data.get("type") == "numpy":
                    new_distribution["kwargs"] = kwargs
                    new_distribution["dist_type"] = distribution_data.get(
                        "numpy_type"
                    )
                else:
                    new_distribution["kwargs"] = kwargs

                distribution_information.append(new_distribution)
            group["dist_info"] = distribution_information
            group_info.append(group)

        return DiseaseStates(
            dist_title=[v for v in distribution_dict.values()],
            group_info=group_info
        )

class ValidateNaturalHistoryGroup:

    @classmethod
    def handle(cls, data: List[dict]) -> NaturalHistory:
        dist_title = [
            "time_dist", "alertness_prob"
        ]
        
        group_info = []
        for history in data:
            for group in history.get("groups"):
                group_info.append(group)
        
        return NaturalHistory(
            dist_title=dist_title,
            group_info=group
        )

class ValidateQuarantineGroups:

    @classmethod
    def handle(cls, general_data: dict, data: List[dict]):
        quarantine_groups = cls._get_quarantine_groups(data)

        if general_data.get("has_cyclic_restrictions"):
            cyclic_data = general_data.get("cyclic_restrictions")
            cls._get_cyclic_policies(
                quarantine_groups,
                cyclic_data.get("variables"),
                data
            )
            cls._get_global_cyclic(general_data)
        if general_data.get("has_tracing_restrictions"):
            cls._get_tracing_policies(
                quarantine_groups,
                cyclic_data.get("")
            )

    @classmethod
    def _get_quarantine_groups(cls, data: List[dict]) -> SimpleGroups:
        names = [group.get("name") for group in data]
        return SimpleGroups(
            names=names
        )

    @classmethod
    def _get_global_cyclic(cls, data: dict) -> GlobalCyclicMR:
        global_cyclic = GlobalCyclicMR(
            enabled=True,
            grace_time=datetime.fromisoformat(data.get("grace_time")),
            global_mr_length=data.get("global_quarantine"),
            global_mr_length_units=data.get("global_quarantine_units"),
            unrestricted_time_mode=data.get("restriction_mode"),
            unrestricted_time=data.get("time_without_restrictions"),
            unrestricted_time_units=data.get("time_without_restrictions_units")
        )
        return global_cyclic

    @classmethod
    def _get_cyclic_policies(
        cls,
        groups: SimpleGroups,
        data: dict,
        group_data: List[dict]
    ) -> dict:
        mr_data = {}
        for group in group_data:
            identifier = group.get("identifier")
            name = group.get("name")
            information = data.get(identifier)
            mr_data.update(
                {name: CyclicMRPolicies(
                    mr_groups=groups,
                    target_group=name,
                    delay=information.get("delay"),
                    delay_units=information.get("delay_units"),
                    mr_length=information.get("length"),
                    mr_length_units=information.get("length_units"),
                    time_without_restrictions=information.get(
                        "unrestricted_time"
                    ),
                    time_without_restrictions_units=information.get(
                        "unrestricted_time_units"
                    )

                )}
            )

        return mr_data

    @classmethod
    def _get_tracing_policies(
        cls,
        groups: SimpleGroups
    ) -> dict:
        pass

class ValidateIsolationAdherenceGroups:
    
    @classmethod
    def handle(cls, data: List[dict]) -> IsolationAdherenceGroups:
        dist_title = "adherence_prob"
        group_info = []
        for group in data:
            distribution_data = group.get("distribution_info")
            group_info.append(distribution_data)
            
        return IsolationAdherenceGroups(
            dist_title=dist_title,
            group_info=group_info
        )
        
class ValidateImmunizationGroups:
    
    @classmethod
    def handle(cls, data: List[dict]) -> ImmunizationGroups:
        dist_title = [
            "immunization_level_dist",
            "immunization_time_distribution"
        ]
        
        group_info = []
        for group in data:
            distribution_data = group.get("distribution_info")
            temp ={
                "name": group.get("name"),
                "dist_info": [data for data in distribution_data]
            }
            group_info.append(temp)
        
        return ImmunizationGroups(
            dist_title=dist_title,
            group_info=group_info
        )
    
class ValidateMobilityGroups:
    
    @classmethod
    def handle(cls, data: List[dict]) -> MobilityGroups:
        dist_title = "mobility_profile"
        group_info = []
        for group in data:
            group_info.append(group)
        
        
        return MobilityGroups(
            dist_title=dist_title,
            group_info=group_info
        )
        
class ValidateMRTPolicies:
    @classmethod
    def handle(cls, data: List[dict]) -> dict:
        policies = {}
        for mrt in data:
            mr_groups = []
            if mrt.get("dead by disease"):
                police = mrt.get("dead by disease")
                mr_groups = SimpleGroups(names=police.get("mr_groups"))
                policies["dead by disease"] = MRTracingPolicies(
                    variable=police.get("variable"),
                    mr_start_level=police.get("mr_start_level"),
                    mr_stop_mode=police.get("mr_stop_mode"),
                    mr_stop_level=police.get("mr_stop_level"),
                    mr_groups=mr_groups,
                    target_groups=police.get("target_groups")
                )
            if mrt.get("diagnosed"):
                police = mrt.get("diagnosed")
                mr_groups = SimpleGroups(names=police.get("mr_groups"))
                
                policies["diagnosed"] = MRTracingPolicies(
                    variable=police.get("variable"),
                    mr_start_level=police.get("mr_start_level"),
                    mr_stop_mode=police.get("mr_stop_mode"),
                    mr_stop_level=police.get("mr_stop_level"),
                    mr_groups=mr_groups,
                    target_groups=police.get("target_groups")
                )
                        
        return policies
    
class ValidateinitialPopulationSetupList:
    
    @classmethod
    def handle(cls, data: List[dict]):
        pass
            
class ValidateConfiguration:
    @classmethod
    def handle(cls, data: dict) -> Configutarion:
        return Configutarion(
            population_number=data.get("population_number"),
            initial_date=data.get("interval_date").get("start"),
            final_date=data.get("interval_date").get("end"),
            iteration_time=data.get("iteration_time"),
            iterations_number=data.get("iteration_number"),
            box_size=data.get("box_size"),
            alpha=0.8,
            beta=0.4
        )
        
class ValidateHealthSystem:
    
    @classmethod
    def handle(cls, data: dict) -> HealthSystem:
        
        return HealthSystem(
            hospital_capacity=data.get("hospital_capacity"),
            ICU_capacity=data.get("ICU_capacity")
        )
