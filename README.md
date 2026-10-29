# Automated\_Trashcan

An Automated Trashcan System IDEA to help improve safety and efficiency of trash/recycling processing. Uses YOLO for object detection and a CNN. Its main purpose is to prevent hazardous items from ever reaching trash compaction.



# Smart Trash Can AI — Project Status

## Project goal

Build a research prototype for an automated trash can that uses computer vision to identify discarded items and choose a disposal action. The design is intended to reflect a possible real-world system, including unknown items, safety-related exceptions, and a configurable disposal policy.

The current plan separates three concerns:

1. **Object detection (YOLO):** locate and identify visible objects.
2. **Material classification (CNN):** estimate a visible item's material where the image supports that judgment.
3. **Control-flow / sorting policy:** combine identity, material, confidence, safety flags, and local disposal rules to select an action or decline to sort.

A camera alone cannot reliably detect every hidden hazard or determine every composite material. A real implementation may need user prompts, additional sensors, and conservative fallback behavior.

## Current environment and project location

* Development environment: Windows PowerShell.
* Python launcher reports Python 3.14.7.
* GPU available: laptop NVIDIA RTX 4070 (training setup planned; not yet verified in this project).
* Project root used in recent commands: `C:\\\\School\\\\AI\\\\Automated\\\_Trashcan`
* TACO annotation folder: `data\\\\raw\\\\taco\\\\TACO\\\\data\\\\`
* Original annotation file: `data\\\\raw\\\\taco\\\\TACO\\\\data\\\\annotations.json`

The actual folder structure should be confirmed before running scripts from another machine or a different project checkout.

## Data acquired so far: TACO

The local `annotations.json` inspection returned:

* **1,500 images listed**
* **4,784 object annotations**
* **60 source categories**

The category-count report was saved as `category\\\_counts.txt`. The complete master taxonomy was generated as `data\\\\manifests\\\\taco\\\_master\\\_taxonomy.csv`.

TACO contains fine-grained litter categories such as cigarette, unlabeled litter, plastic film, clear plastic bottle, other plastic, plastic wrapper, drink can, plastic bottle cap, plastic straw, broken glass, glass bottle, disposable plastic cup, paper, cartons, bags, containers, and battery.

Important counts observed in the report:

* Cigarette: 667 annotations
* Unlabeled litter: 517
* Plastic film: 451
* Clear plastic bottle: 285
* Other plastic: 273
* Other plastic wrapper: 260
* Drink can: 229
* Plastic bottle cap: 209
* Plastic straw: 157
* Broken glass: 138
* Glass bottle: 104
* Disposable plastic cup: 104
* Battery: 2
* Tupperware: 4
* Other plastic cup: 2
* Food waste: 8

Counts are annotations, not unique objects or unique images. They do not by themselves establish class balance, label correctness, or model performance.

## Scripts and artifacts created

* `scripts\\\\build\\\_class\\\_mapping.py`  
Generates a provisional master taxonomy from TACO's category list and annotations.
* `data\\\\manifests\\\\taco\\\_master\\\_taxonomy.csv`  
Contains 60 source categories and columns for source category ID/name, proposed object identity, provisional material, handling flag, annotation count, readiness status, and notes.
* `scripts\\\\make\\\_taco\\\_review\\\_sheet.py`  
Creates `results\\\\taco\\\_category\\\_review.jpg`, a first-pass contact sheet with one selected annotated example per category where available.
* `results\\\\taco\\\_category\\\_review.jpg`  
Visual review aid. It is not a complete annotation audit. The same source image can appear for more than one category, and the first selected annotation is not necessarily representative of the whole category.
* `data\\\\manifests\\\\taco\\\_class\\\_mapping.csv`  
An earlier, more limited draft mapping. Prefer the newer `taco\\\_master\\\_taxonomy.csv` as the working inventory, and do not use either file as final training labels without review.

## Decisions made so far

1. Preserve all 60 TACO source categories in the master inventory rather than deleting rare categories.
2. Keep **object identity**, **material**, **hazard/handling**, and **disposal action** as separate concepts.
3. Treat material assignments as provisional until sample images and source annotations are reviewed.
4. Do not automatically map `Unlabeled litter` to a known material or object class.
5. TACO has only two battery annotations in this local report, so it is insufficient by itself for a reliable battery detector. Battery/e-waste and other safety-critical categories need additional data and careful evaluation.
6. The disposal controller should support uncertain/unknown items, request another view when feasible, and route to a safe hold/reject/manual-review path when it cannot make a defensible decision.
7. Disposal rules must be configurable for the target location; material classification alone does not determine whether an item is accepted for recycling.

## Important corrections / unresolved issues

* **No YOLO conversion has been run yet.** The proposed shortlist is not a final class list.
* **No train/validation/test split has been created yet.**
* **No model has been trained or evaluated yet.**
* The current material mappings are provisional and may be wrong for composite packaging or visually ambiguous items.
* The first contact sheet shows only one selected example per category; it cannot prove that every annotation in a class is correct.
* Before splitting, inspect source image paths and annotation validity. Group related images and ensure images/crops from the same source do not cross data splits.
* Check each dataset's license and attribution requirements before use or redistribution. Public download does not automatically mean unrestricted reuse.
* Python 3.14.7 is installed. Before choosing training dependencies, verify that the intended PyTorch, Ultralytics, TensorFlow, and image-processing versions support the selected Python version. A separate compatible virtual environment may be preferable.
* The planned YOLO class shortlist discussed so far is only a candidate. It should be revised after reviewing counts, visual examples, annotation quality, intended object identity, and safety requirements. Do not train on `Unlabeled litter` as if it were a known object class.

## Proposed next steps

1. Audit the master taxonomy and representative images; correct questionable material assignments and define explicit handling flags.
2. Inspect image paths, bounding boxes, category mappings, and duplicate/related images.
3. Choose a versioned initial YOLO class set while preserving the full taxonomy for future expansion.
4. Create a reproducible train/validation/test split before augmentation, with grouping to prevent leakage.
5. Convert only approved categories to YOLO labels and validate the converted labels visually.
6. Prepare a separate CNN material-classification dataset with verified labels and source-image provenance.
7. Add supplemental battery/e-waste examples and build a real-world held-out test set.
8. Implement and test the control-flow rules before treating any model prediction as an automatic disposal command.

## Current status

**Data inspection and preliminary taxonomy only.** The source TACO annotations have not been modified. No training labels, data splits, or trained models have been finalized.



