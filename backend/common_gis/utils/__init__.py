import enum
from common_gis.models import (PublishedComputation, PublishedComputationYear)

def get_published_computation_by_change_enum(change_enum_str):
	"""Get associated Published computation by enum type

	Args:
		change_enum (_type_): _description_
	"""
	return PublishedComputation.objects.filter(computation_type=change_enum_str).first()

	# def _is_instance(enum_type):
	# 	for member in change_enum:
	# 		return isinstance(member, enum_type)
	# 	return False
	
	# if _is_instance(LulcChangeEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.LULC.value).first()

	# if _is_instance(ForestChangeEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.FOREST_CHANGE.value).first()

	# # if _is_instance(ForestChangeEnum):
	# # 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.FOREST_FIRE.value).first()

	# if _is_instance(FireRiskEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.FOREST_FIRE_RISK.value).first()

	# if _is_instance(SOCChangeEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.SOC.value).first()
	
	# if _is_instance(ProductivityChangeBinaryEnum) or _is_instance(ProductivityChangeTernaryEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.PRODUCTIVITY_STATE.value).first()
	
	# if _is_instance(TrajectoryChangeBinaryEnum) or _is_instance(TrajectoryChangeTernaryEnum) or _is_instance(TrajectoryChangeQuinaryEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.PRODUCTIVITY_TRAJECTORY.value).first()
	
	# if _is_instance(PerformanceChangeBinaryEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.PRODUCTIVITY_PERFORMANCE.value).first()
	
	# if _is_instance(ProductivityChangeBinaryEnum) or _is_instance(ProductivityChangeTernaryEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.PRODUCTIVITY.value).first()
	
	# if _is_instance(LandDegradationChangeEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.LAND_DEGRADATION.value).first()
	
	# if _is_instance(AridityIndexEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.ARIDITY_INDEX.value).first()
	
	# if _is_instance(ClimateQualityIndexEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.CLIMATE_QUALITY_INDEX.value).first()
	
	# if _is_instance(SoilQualityIndexEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.SOIL_QUALITY_INDEX.value).first()
	
	# if _is_instance(VegetationQualityEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.VEGETATION_QUALITY_INDEX.value).first()
	
	# if _is_instance(ManagementQualityIndexEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.MANAGEMENT_QUALITY_INDEX.value).first()
	
	# if _is_instance(ESAIEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.ESAI.value).first()
	
	# if _is_instance(ForestChangeTernaryEnum) or _is_instance(ForestChangeQuinaryEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.FOREST_CARBON_EMISSION.value).first()
	
	# if _is_instance(ILSWEEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.ILSWE.value).first()
	
	# if _is_instance(RUSLEEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.RUSLE.value).first()
	
	# if _is_instance(CVIEnum):
	# 	return PublishedComputation.objects.filter(computation_type=ComputationEnum.COASTAL_VULNERABILITY_INDEX.value).first()