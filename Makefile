.PHONY: demo test verify

demo:
	python scripts/generate_synthetic_data.py
	PYTHONPATH=src python -m hvac_mapping.cli --points data/synthetic/bas_points.csv --schedule data/synthetic/equipment_schedule.csv --output-dir outputs/demo

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

verify: demo test
