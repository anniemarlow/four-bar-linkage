import numpy as np
import pandas as pd
import math as math
import matplotlib.pyplot as plt
import scipy.optimize
import time



def check_valid(l1, l2, l3, l4):
    """Check if the entered link lengths meet the constraint specified in the project. 
    
    Parameters
    ----------
    l1 : int or float
        Entered length of link 1. 
    l2 : int or float
        Entered length of link 2.
    l3 : int or float
        Entered length of link 3.
    l4 : int or float
        Entered length of link 4.
    
    Returns
    -------
    boolean True/False 
        True: link lengths are valid.
        False: link lengths are not valid.
    """
    
    # convert link lengths to floats
    l1 = float(l1)      # link 1
    l2 = float(l2)      # link 2
    l3 = float(l3)      # link 3
    l4 = float(l4)      # link 4
    
    links = [l1,l2,l3,l4]
    
    # find maximum and minimum link lengths
    link_max = max(links)
    link_min = min(links)
    pos_max = links.index(link_max)
    pos_min = links.index(link_min)
    
    # create list to store max and min lengths
    min_max = [link_min, link_max]
    
    # convert links list to only links that are not max or min links
    del links[pos_max]
    
    if pos_max < pos_min:
        del links[pos_min-1]
        
    elif pos_max >= pos_min:
        del links[pos_min]
    
    # check if link lengths are valid given constraint
    if sum(min_max) <= sum(links):
        return True
    
    elif sum(min_max) > sum(links):
        return False

    

def calculate_linkage(l1, l2, l3, l4):
    """Calculate positions of links for a mechanism rotation of 360 degrees. Generate animation to show mechanism rotation.
    
    Each link position is defined by an angle (theta1, theta2, theta3, and theta4). This function uses Freudenstein's equation to solve for theta4 given a value of theta2 between 0 and 360 degrees (one full rotation). Theta4 and theta2 are then used to solve for theta3 so that each link will have a stored list of theta values that define their position during a full rotation of theta2. These lists of theta values are used to animate the link positions. 
    
    Parameters
    ----------
    l1 : int or float
        Entered length of link 1. 
    l2 : int or float
        Entered length of link 2.
    l3 : int or float
        Entered length of link 3.
    l4 : int or float
        Entered length of link 4.
    
    Returns
    -------
    linkage : html animation
        Animation showing the mechanism motion.
        
    Acknowledgements
    ----------------
    Code used to generate and display the animation was drawn from this tutorial by Jeffrey Kantor (https://jckantor.github.io/CBE30338/A.03-Animation-in-Jupyter-Notebooks.html).
    """
    
    # define parameters L1, L2, and L3 from link lengths (to be used later)
    L1 = l1/l4
    L2 = l1/l2
    L3 = (l1**2 + l2**2 - l3**2 + l4**2)/2/l2/l4

    # calculate minimum and maximum values for theta4
    try:
        theta4_min = math.degrees(math.acos( ((l2 - l3)**2 - l1**2 - l4**2)/(2*l1*l4) ))
        theta4_max = math.degrees(math.acos( ((l2 + l3)**2 - l1**2 - l4**2)/(2*l1*l4) ))
    except:
        print('')
        print('oops! due to geometry constraints, we cannot calculate the motion for this set of links.')
        time.sleep(2.75)
        print('')
        print('please enter a new set of link lengths.')
        print('')
        linkage = False
        return linkage

    # create empty lists for theta4 and theta3
    theta4 = []
    theta3 = []

    # use root solver to solve for theta4 given value of theta2 and initial guess of theta4_max
    for theta2 in range(0, 361):
        
        # freudenstein's equation for four-bar linkage mechanisms 
        freudenstein = lambda theta4 : L3 + L2*math.cos(math.radians(theta4)) - L1*math.cos(math.radians(theta2)) - \
            math.cos(math.radians(theta2 - theta4))

        theta4_sol = scipy.optimize.fsolve(freudenstein, theta4_max) 

        theta4.append(theta4_sol)
        
        # calculate theta3 values for each value of theta4 and theta2
        try:
            
            if l2*math.cos(math.radians(360-theta2)) > l1-l4*math.cos(math.radians(180-theta4[theta2])):
                theta3.append(180-math.asin( (l4*math.sin(math.radians(theta4[theta2])) - l2*math.sin(math.radians(theta2)))/l3 ))
                
            else:
                theta3.append(math.asin( (l4*math.sin(math.radians(theta4[theta2])) - l2*math.sin(math.radians(theta2)))/l3 ))
        
        except:
            print('')
            print('oops! due to geometry constraints, we cannot calculate the motion for this set of links.')
            time.sleep(2.75)
            print('')
            print('please enter a new set of link lengths.')
            print('')
            linkage = False
            return linkage
    
    # set up plot for animation
    # set axis limits
    x_neg = -1.25*l2
    x_pos = 1.25*(l1 + l4)
    y_neg = -1.25*l2
    y_pos = 1.25*l4

    if x_neg > y_neg:
        y_neg = x_neg
        
    else:
        x_neg = y_neg
        
    if x_pos >  y_pos:
        y_pos = x_pos
        
    else:
        x_pos = y_pos

    # create a figure and axes
    fig = plt.figure(figsize=(12,5))
    ax = plt.subplot(1,1,1)  

    ax.set_xlim([x_neg,x_pos])
    ax.set_ylim([y_neg, y_pos])
    ax.set_aspect('equal', 'box')

    # create objects that will change in the animation
    # these are initially empty, and will be given new values for each frame in the animation
    line1, = ax.plot([], [], 'tab:brown', lw=7)     # ax.plot returns a list of 2D line objects
    line2, = ax.plot([], [], 'tab:cyan', lw=7)
    line3, = ax.plot([], [], 'tab:pink', lw=7)
    line4, = ax.plot([], [], 'tab:green', lw=7)

    # animation function. This is called sequentially
    def drawframe(n):
        
        x1 = np.array([0, l1])
        y1 = np.array([0, 0])
        x2 = np.array([0, l2*math.cos(math.radians(n))])
        y2 = np.array([0, l2*math.sin(math.radians(n))])
        x3 = np.array([l2*math.cos(math.radians(n)), l1 + l4*math.cos(math.radians(theta4[n]))])
        y3 = np.array([l2*math.sin(math.radians(n)), l4*math.sin(math.radians(theta4[n]))])
        x4 = np.array([l1, l1 + l4*math.cos(math.radians(theta4[n]))])
        y4 = np.array([0, l4*math.sin(math.radians(theta4[n]))])
        line1.set_data(x1, y1)
        line2.set_data(x2, y2)
        line3.set_data(x3, y3)
        line4.set_data(x4, y4)

        return (line1,line2,line3,line4)

    # close plot of last frame of animation
    plt.close()

    # create animation
    from matplotlib import animation

    # blit=True re-draws only the parts that have changed.
    anim = animation.FuncAnimation(fig, drawframe, frames=360, interval=20, blit=True)

    # display animation
    from IPython.display import HTML
    
    linkage = HTML(anim.to_html5_video())
    
    return linkage
    

def four_bar_linkage():
    """Main function to run four-bar linkage simulator. 
    
    Parameters
    ----------
    None.
    
    Returns
    -------
    linkage : html animation 
        linkage is generated from function calculate_linkage.
    """
    
        
    t = 2.75    # standard pause time between print statements
    ts = 1      # shorter pause

    # start info
    print('welcome to the four-bar linkage simulator!')
    time.sleep(ts)
    print('')
    print('you will enter a length for each of the four links and this code will generate an animation of how your mechanism will operate.')
    time.sleep(t)
    print('')
    print('there is one constraint to note before you enter your link lengths:')
    time.sleep(t)
    print('the sum of the shortest and longest links must be less than or equal to the sum of the other two links for full mechanism rotation.')
    time.sleep(t)
    print('')
    
    # True while linkage is being generated 
    calculating = True
    
    while calculating:
    
        # True while link lengths are not entered or invalid given constraint
        not_valid = True
        
        while not_valid: 

            print('to start, enter a length for link 1.')
            print('if you are stuck, try: 2.7, 1, 2.4, 3')

            # get a length for link 1 from the user
            l1 = input('link 1 :\t')

            print('')
            print('great! for link 2, enter a length shorter than link 1.')

            l2 = input('link 2 :\t')
            
            print('')
            print('finally, enter lengths for links 3 and 4. remember the constraint.')

            l3 = input('link 3 :\t')

            l4 = input('link 4 :\t')
            
            # tell user that code will check validity of link lengths
            print('')
            print('now that we have set the link lengths, we need to check to see if they create a valid four-bar linkage given our constraint.')
            time.sleep(t)
            print('')
            print('we will now check if we have a valid four-bar linkage:')
            time.sleep(ts)
            print('calculating ...')
            time.sleep(1)
            print('')
            
            # check validity of link lengths
            validity = check_valid(l1, l2, l3, l4)
            
            # proceed if links are valid; return to entering link lengths if invalid
            if validity:
                not_valid = False
                
            elif not validity:
                print('invalid four-bar linkage! the sum of the shortest and longest links must be less than or equal to the sum of the other two links.')
                time.sleep(t)
                print('')
                print('please reenter link lengths to satisfy our constraint.')
        
        # when entered link lengths are valid, calculate linkage mechanism motion and generate animation:
        print('link lengths are valid!')
        time.sleep(ts)
        print('')
        print('now, the code will solve for the allowed ranges of motion for each link and generate a list of positions.')
        time.sleep(t)
        print('')
        print('the code will use the generated link positions to animate the motion of the linkage.')
        time.sleep(t)
        print('')
        print("let's look at our four-bar linkage!")
        time.sleep(ts)
        print('preparing four-bar linkage ... (this may take a few seconds)')
        
        # convert link lengths to floats for use in calculate_linkage function
        l1 = float(l1)
        l2 = float(l2)
        l3 = float(l3)
        l4 = float(l4)

        linkage = calculate_linkage(l1, l2, l3, l4)
        
        # if animation is generated, end function and return linkage. if error, return to entering link lengths
        if linkage:
            calculating = False
            
    return linkage


