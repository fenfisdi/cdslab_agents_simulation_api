from datetime import datetime
from typing import List
from uuid import uuid1

from abmodel.models.base import SimpleGroups
from abmodel.models.disease import (
    DiseaseStates,
    NaturalHistory,
    SusceptibilityGroups
)
from abmodel.models.mobility_restrictions import CyclicMRGroups, GlobalCyclicMR


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
        pass


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
            print("Tambien")

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
                {name: CyclicMRGroups(
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
