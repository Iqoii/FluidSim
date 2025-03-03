# FluidSim
Some fluid simulation stuff I've worked on for fun about a year ago (March/April 2024). Really difficult stuff actually, I still have nightmares with the Navier-Stokes equations.

DISCLAIMER: You need pygame, sys and math (pygame is the only none standard I think) to run this.

This project is a 2D fluid simulation implemented using Python and Pygame. It simulates the behavior of fluid particles using a simplified version of the Smoothed Particle Hydrodynamics (SPH) method. 

    Mouse: Repel particles by clicking and dragging.

    Keyboard:

        0: Stop all particles.

        1: Resume particle movement.

        2: Enable gravity.

        3: Disable gravity.

        4: Set low pressure (smoother fluid).

        5: Set high pressure (stiffer fluid).

Inspired by this video:

https://www.youtube.com/watch?v=rSKMYc1CQHE&t=1961s

I alse read and understood some (but definitely not all) elements from this:

https://sph-tutorial.physics-simulation.org/pdf/SPH_Tutorial.pdf

I also used AI to help me out sometimes even though it wasn't that good at coding when I did this... 
