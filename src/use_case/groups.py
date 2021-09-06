from typing import List
from uuid import uuid1

from abmodel.models.base import SimpleGroups
from abmodel.models.disease import DiseaseStates, SusceptibilityGroups


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
