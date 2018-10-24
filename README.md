# NaiveTurk

An early attempt at tracking bots on Mechanical Turk. No longer under development (see Status section).

## History

This git repository represents the resting place of an early prototype of a Mechanical Turk bot tracker that I had developed. The initial impetus for this project was to determine how naive Mechanical Turk workers were or were not. One possible issue regarding Mechanical Turk use for psychology researchers is that many reesarchers may be using the same basic paradigm. Some paradigms are potentially aimed at naive participants with little knowledge of what variables are being manipulated. Unfortunately, there is no built-in ability to track which workers have potentially completed a related task. This app would have functioned as a database to keep track of the activity status of active workers. It would have served as the worker equivalent to TurkOpticon. 

Early on into the development of the naivety tracker portion of this application, we realized that there was really no foolproof means of preventing data misuse by researchers or other interested parties. Therefore, we began thinking of ways to use our API as a bottracker that would compile quality ratings over time – this type of API would require much less personal data sharing than the original naivety tracker idea. 

Although we were hashing all relevant data serverside, so that a database breach would not be fatal to user confidentiality, ultimately we did not feel comfortable collecting this bot tracking data either. 

## Status

This project is no longer under development as I realized that it was too fraught with potential ethical, privacy, and IRB-related issues. 


## Function

The bot tracker works as an API that would have been called at the beginning of each HIT. The API is very simple. Each call at the beginning of a HIT would include just the worker's MTurk ID. This would be used to query the database for extant information on that worker's successful HIT completion rate and which HITs they had previously completed. 

# Alternatives

* TurkPrime
* https://rkennedy.shinyapps.io/IPlookup/
* Simply raising your worker requirements (e.g., Number of HITs completed and successful completion rate)
* Paying workers more in order to allow for thoughtful completion of tasks.

And always remember to avoid the [data industrial complex](https://techcrunch.com/2018/10/24/apples-tim-cook-makes-blistering-attack-on-the-data-industrial-complex/).
