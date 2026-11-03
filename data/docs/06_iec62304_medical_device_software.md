# IEC 62304 – Medical Device Software Life Cycle Processes

## Scope
IEC 62304:2006+A1:2015 defines life cycle requirements for the development and maintenance of medical device software, both software embedded in a device and software that is itself a medical device (Software as a Medical Device, SaMD). It is recognized by FDA as a consensus standard and harmonized in the EU. It assumes the manufacturer operates a quality management system (such as ISO 13485) and a risk management process according to ISO 14971.

## Software Safety Classification
Each software system is assigned a safety class based on the possible effects on the patient, operator or other people resulting from a hazard the software can contribute to:
- Class A: no injury or damage to health is possible.
- Class B: non-serious injury is possible.
- Class C: death or serious injury is possible.
Amendment 1 (2015) allows the manufacturer to consider risk control measures external to the software system (for example, a hardware watchdog) when determining the class. The safety class determines which process activities and documentation are required; for example, detailed design of software units is required for Class C, and software unit verification acceptance criteria are required for Classes B and C.

## Life Cycle Processes
The standard defines five processes: Software development (clause 5: planning, requirements analysis, architectural design, detailed design, unit implementation and verification, integration and integration testing, system testing, and release); Software maintenance (clause 6); Software risk management (clause 7), including analysis of software contributing to hazardous situations; Software configuration management (clause 8); and Software problem resolution (clause 9).

## SOUP
SOUP (Software Of Unknown Provenance) is a software item already developed and generally available that was not developed for the purpose of being incorporated into the medical device, or previously developed software for which adequate records of the development processes are not available. Manufacturers must identify each SOUP item with its title, manufacturer and version, specify functional and performance requirements and the hardware and software it needs, and evaluate published anomaly lists for SOUP items for Class B and C software.

## FDA Software Documentation Levels
FDA's guidance "Content of Premarket Submissions for Device Software Functions" (final, June 2023) replaced the 2005 "Level of Concern" approach with two documentation levels: Basic and Enhanced. Enhanced Documentation is required when a failure or flaw of the device software function could present a hazardous situation with a probable risk of death or serious injury, either before implementation of risk control measures, to a patient, user of the device, or others in the environment of use. Enhanced documentation includes, among other things, a software design specification and a complete list of software anomalies, in addition to the documentation elements provided at the Basic level.
