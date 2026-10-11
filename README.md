# Can a Short Touch Predict a Slide?

Could one short touch tell a robot how hard it is to slide across a new surface, or how far a moving object will travel before stopping? This experiment will test that idea.

**Status: proposed experiment, researched on 10 October 2026. We have no force or motion results from this experiment yet.**

## The goal

We want robot simulations to adapt to real surfaces. A **physics engine** calculates forces and movement; a **world model** predicts what an action will do.

We will start with sliding contact between one fixed pad and different surfaces. Friction depends on both things touching and the contact conditions. [NIST explains this dependence](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication960-11.pdf).

## What we will do

We will work through three tests:

1. **Predict resistance.** Use a short initial touch to predict friction forces during independent later slides at other speeds and pressing forces.
2. **Predict movement.** Put the estimated friction into a small simulator. Check its predicted position, speed and stopping distance against a real moving object.
3. **Check usefulness.** If predictions improve, test whether the model helps move an object to a target.

We will start with flat, rigid surfaces, one direction and the same pad throughout. The force test can use a motorized slide. The movement test needs an object whose motion actually responds to forces.

**Half a second of steady sliding** is our proposed initial observation budget. We will test whether it is enough and report the full probing time and travel.

## Why we are doing this

Our [earlier vibration project](https://github.com/EltonChang1/tactile-contact-research/blob/c6fee1245a86bd45c3a6bcbe16c838e1b4a4c5d9/README.md) predicts vibrations from recorded touches. Here we will test physical forces and movement: how much touching is necessary, which measurements help, and whether complicated models improve on simple estimates.

## What we will compare

- **One general setting:** use the same friction setting for every surface.
- **A simple brief-touch estimate:** calculate friction from measured forces during the initial touch.
- **A tactile-based estimate:** predict friction from vibrations or tactile readings, compared with using the known conditions alone.
- **A longer calibration:** use more touches as a reference and report the extra time and data.

Independent force measurements will train and check the methods. We will separately compare force readings alone with force plus tactile readings to test tactile's added value.

Useful force calibration and useful tactile information are separate findings. **A simple method can achieve the goal even if AI adds no benefit.**

## How we will make the test fair

We will keep entire surfaces out of model training. Brief-touch methods get only the allowed initial touch on each new surface. The longer-calibration reference gets its declared extra touches; later test trials stay hidden until evaluation.

We will calibrate the measurements, verify timing and use independent repetitions. Before the final test, we will fix the rules and the improvement needed to matter in practice.

## What the results would mean

| Possible finding | What it would support |
| --- | --- |
| A brief force estimate improves on the general setting | Rapid contact calibration helps. |
| Tactile readings improve the appropriate comparison | The tactile signal supplies useful mechanical information. |
| The estimates improve real movement predictions | We have evidence for a small contact world model. |
| The model improves the target task | It has practical value for that task. |
| Improvements are too small or uncertain | We should examine the measurements, touch budget and model before expanding the study. |

## What the research tells us

Related systems already show promising results. [DiffTactile](https://arxiv.org/html/2403.08716v1) fits contact physics using real measurements. [RoboPack](https://www.roboticsproceedings.org/rss20/p130.html) uses tactile information for motion prediction and robot pushing and packing.

Our study will test very short touches on new surfaces against strong simple methods. It must establish its own answer.

## Where we are now

This repository contains the new experiment design. Implementation and data collection are the next work.

The [earlier vibration project](https://github.com/EltonChang1/tactile-contact-research/blob/c6fee1245a86bd45c3a6bcbe16c838e1b4a4c5d9/README.md) has working vibration-prediction software and checked results. Mechanical data, rig access and force calibration remain unconfirmed.

**First, verify a usable dataset or rig.** The Penn Haptic Texture Toolkit is a promising recorded-data candidate, pending access and measurement checks. The complete movement test needs additional capabilities.

See the [methods and research review](docs/methods.md) for data candidates, calibration, trial design, evaluation and sources. This follows Stages B and C of the [research plan](https://github.com/EltonChang1/tactile-contact-research/blob/c6fee1245a86bd45c3a6bcbe16c838e1b4a4c5d9/docs/research_plan.md) and the mechanical steps in the [implementation guide](https://github.com/EltonChang1/tactile-contact-research/blob/c6fee1245a86bd45c3a6bcbe16c838e1b4a4c5d9/docs/implementation_guide.md).

The [origin note](docs/origin.md) records where this design came from.
