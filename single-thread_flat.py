import time
import math
import tweepy
import os 
import datetime
from requests.exceptions import Timeout, ConnectionError
from requests.packages.urllib3.exceptions import ReadTimeoutError
import ssl
import pickle

#=================Global parameters===================#
status_max = [75000, 75000, 3200]       # the max timelines that tweet allowed to call is 3200
first_seed_user = "1074719328"			# Amyhuser = "1074719328"
seed_followers_list = []                 # Brogan: user_id = 252883041 screen_name = brogiebee good = 19778974 good_name=jbwilson3791
seed_friends_list = []
time_now = datetime.datetime.now()

#===============Show all the brogiebeeOAuths===================#
consumer_key = ["your key1", "your key2" ...]

consumer_secret = ["your secret1", "your secret2", ...]

access_token = ["token1", ...]

access_token_secret = ["token secret1", ...]


#============================Userd for test================================#
def Print_Result(list):
	for l in list:
		print(str(l))
	print('Rresult Print Finished!')

#==============Change OAuth and build new api======================#
def Authentication(order):
    auth = tweepy.OAuthHandler(consumer_key[order], consumer_secret[order])
    auth.set_access_token(access_token[order], access_token_secret[order])
    api = tweepy.API(auth)
    print("Create api!")
    return api

#------------------------------------Change api------------------------------------------------#
def Change_api(api,order):
	order += 1
	if order > len(consumer_key)-1:
		order = 0
	api = Authentication(order)
	return api, order

#=======================Check rate limit and remaining of different items======================#
#-------put these items into a list, thus different remaings's order as:-----------------------#
#----Follower->0; Friends->1; home_line->2, such as:[[15, 5],[15, 10],[15,2]]------------------#
#==============================================================================================#
def Check_limit(api,which): #check followers, friends, statuses, favorites, lists, list_members
    status_now = []
    data = api.rate_limit_status()      #check_status
    status_now.append([data['resources']['followers']['/followers/ids']['limit'],		#max: 15: 15pages*5000ids/page
					  data['resources']['followers']['/followers/ids']['remaining'],
					  data['resources']['followers']['/followers/ids']['reset']])
    status_now.append([data['resources']['friends']['/friends/ids']['limit'],			#max: 15: 15pages*5000ids/page
					  data['resources']['friends']['/friends/ids']['remaining'],
					  data['resources']['friends']['/friends/ids']['reset']])
    status_now.append([data['resources']['statuses']['/statuses/user_timeline']['limit'],		#max: 180: 180pages*20pieces/page
					  data['resources']['statuses']['/statuses/user_timeline']['remaining'],
					  data['resources']['statuses']['/statuses/user_timeline']['reset']])
    status_now.append([data['resources']['favorites']['/favorites/list']['limit'],		#max: 180: 180pages*20pieces/page
					  data['resources']['favorites']['/favorites/list']['remaining'],
					  data['resources']['favorites']['/favorites/list']['reset']])
    status_now.append([data['resources']['lists']['/lists/list']['limit'],
    				  data['resources']['lists']['/lists/list']['remaining'],
    				  data['resources']['lists']['/lists/list']['reset']])
    status_now.append([data['resources']['lists']['/lists/members']['limit'],
    				  data['resources']['lists']['/lists/members']['remaining'],
    				  data['resources']['lists']['/lists/members']['reset']])
    return status_now[which]

#===============================Compare whether need new authentication======================#
def Compare_Remain(status,total,per_page,max_record,order):
	have = status[1]*per_page
	if total>max_record:
		print("Total is %s, exceed max record %s"%(total,max_record))
		total = max_record
	else:
		print("We need %s, still have %s"%(total,have))
	if have > total:
		print("Enough rate, no need to change api")
		api = Authentication(order)
	else:
		order = order + 1
		if order > len(consumer_key)-1:
			order = 0
		print("Not enough rate, change api")
		#print("order in func: %s" %order)
		print(datetime.datetime.now())
		api = Authentication(order)
	return api, order, total

#============================Fetch User Profile============================#
#-----profile includes(this order): id, name, screen_name, description,
#-----Language, account created at, location, time_zone, number of tweets,
#-----# of followers, # of followings, # of listed(# of user is listed) 
#==========================================================================#
def getProfile(api, user_id, newpath):
	user = api.get_user(user_id)
	whole_profile = user._json
	profile = {}
	profile['id']=user.id
	profile['name']=user.name
	profile['screen_name']=user.screen_name
	profile['description']=user.description
	profile['created_at']=user.created_at
	profile['language']=user.lang
	profile['location']=user.location
	profile['time_zone']=user.time_zone
	profile['statuses_count']=user.statuses_count
	profile['followers_count']=user.followers_count
	profile['friends_count']=user.friends_count
	profile['listed_count']=user.listed_count
	profile['favourites_count']=user.favourites_count
	pickle.dump(profile, open(newpath+'/profile.pickle', 'wb'))
	pickle.dump(whole_profile, open(newpath+'/whole_profile.pickle', 'wb'))
	print("Profile created successfully!")
	return profile

#=================== fetch followers_list==========================#
def getFollowers(api, user_id,newpath):
	followers_list = []
	pages = tweepy.Cursor(api.followers_ids, id=user_id).pages()
	i=1
	ids = []
	while (i > 0):
		try:
			page = next(pages)
			print(i)
			i = i-1
			followers_list.extend(page)
			pickle.dump(page,open(newpath+'/followers_list.pickle','ab'))
		except  tweepy.RateLimitError:
			print("# of followers of user: %s exceed max rate, must to sleep" %user_id)
			time.sleep(60*5)
		except tweepy.TweepError as e:
			print("Followers Strange error! Try to sleep for 15 minutes...")
			print (e)
			time.sleep(5*60)
		except StopIteration:   # To the end of next function
			print("Successfully Record all followers of user: %s" %user_id)
			break
	return followers_list   

#=================== fetch friends_list==========================#
def getFriends(api, user_id,newpath):
    friends_list = []
    pages = tweepy.Cursor(api.friends_ids, id=user_id).pages()   
    i=1
    ids = []
    while (i > 0) :
        try:
            page = next(pages)
            print(i)
            i = i-1
            friends_list.extend(page)
            pickle.dump(page,open(newpath+'/friends_list.pickle','ab'))
        except tweepy.RateLimitError:
        	print("# of friends of user: %s exceed max rate, must to sleep" %user_id)
        	time.sleep(60*5)
        except tweepy.TweepError as e:
        	print("Friends Strange error! Try to sleep for 15 minutes...")
        	print (e)
        	time.sleep(5*60)
        except StopIteration:   # To the end of next function
        	print("Successfully Record all friends of user: %s" %user_id)
        	break
    return friends_list   

#========================Get Statuses===================================#
def getStatuses(api,user_id,newpath,total):
	status = {}
	page = []
	pages = tweepy.Cursor(api.user_timeline, id=user_id).pages()
	i=math.ceil(total/20)
	while (i > 0):
		try:
			page = next(pages)
			print(i)
			i = i-1
			pickle.dump(page,open(newpath+'/statuses_list.pickle','ab'))	#Record all the statuses of user
		except tweepy.RateLimitError:
			print("This shouldn't happen, but it shows you exceed the statuses rate limit!")
			time.sleep(60*15)
		except tweepy.TweepError as e:
			print (e)
			if str(e) == "Twitter error response: status code = 429":
				print("Too many request, try to sleep 5 mins")
				time.sleep(60*5)
		except StopIteration:			
			print("Successfully Record all status of user: %s" %user_id)
			break

#========================get list members=======================#
def getList(api,user_id,newpath,order):
	list_ids = []
	list_member_count = []
	members_sum = 0
	list_page = 1
	while True:
		try: 
			lists_all = api.lists_all(user_id=user_id,page=list_page)
			if lists_all:
				for plist in lists_all:
					print(plist.name)
					pickle.dump(plist,open(newpath+'/lists.pickle','ab'))
					list_ids.append(plist.id)
					list_member_count.append(plist.member_count)
			else:	
				break
			list_page += 1
		except tweepy.TweepError as e:
			print(e, "Try to change api")
			(api,order) = Change_api(api,order)
	l = 0
	list_members = []
	for list_id in list_ids:
		pickle.dump("list: %s"%list_ids[l],open(newpath+'/list_members.pickle','ab'))
		status=Check_limit(api,4)
		(api,order,members_total) = Compare_Remain(status,list_member_count[l],20,300,order)
		member_pages = tweepy.Cursor(api.list_members, list_id = str(list_ids[l])).pages()
		while True:
			try:
				member_page = next(member_pages)
				for member in member_page:
					member_id = member.id
					list_members.append(member_id)
					pickle.dump(member_id,open(newpath+'/list_members.pickle','ab'))
				else:
					break
			except StopIteration:
				print("Finish list member record!")
				break
			except tweepy.error.RateLimitError:
				print(e, "Rate Limit Error: Try to sleep for 15 minutes")
				time.sleep(60*15)
			except tweepy.TweepError as e:
				if str(e) == "[{'message': 'Sorry, that page does not exist.', 'code': 34}]"or\
							"[{'code': 34, 'message': 'Sorry, that page does not exist.'}]":
					print("List blongs to protected user!")					
					break
				else:
					print(e, "Strange Error: Try to sleep for 15 minutes")
					time.sleep(60*15)
		l += 1
	return api, order, list_members

#====================Get all the favorited(like)=========================================#
def getLikes(api,user_id,newpath,order):
	page = 1
	while True:
		try:
			likes = api.favorites(user_id = user_id, page = page)
			print("Page: %s"%page)
			if likes:
				for like in likes:
					pickle.dump(like._json,open(newpath+'/likes_list.pickle','ab'))	#Record all the statuses of user
			else:
				print("Successfully Record all likes of user: %s" %user_id)
				break
			page += 1
		except tweepy.RateLimitError as e:
			print(e, "Try to change api!")
			(api,order)=Change_api(api,order)
		except tweepy.TweepError as e:
			print (e, "Try to change api!")
			(api,order)=Change_api(api,order)
	return api,order

#========Find the user both in followers_list and friends_list(followings_lsit)=================#
def F_and_F(followers_list,friends_list,list_members):	
	fing_list = []
	ff_list = []
	fer_bn_fing = []
	fing_bn_fer = []
	fing_list = set(friends_list) | set(list_members)
	ff_list = set(followers_list) & set(fing_list)
	fer_bn_fing = set(followers_list) - set(ff_list)
	fing_bn_fer = set(fing_list) - set(ff_list)
	return ff_list, fer_bn_fing, fing_bn_fer

def create_path(path1="Data", path2=""):
	newpath = r'%s/%s'%(path1,path2)
	if not os.path.exists(newpath):
		os.makedirs(newpath)
	return newpath

#========================crawl just one user at one time======================#
def crawl_single(user_id,newpath,api,order):
	user_followers_list = []
	user_friends_list = []
	user_list_members = []
	newpath = r'Data/%s'%(user_id)
	try:
		if os.path.exists(newpath):		#if folder already exists, don't crawl again; if tweets_count = 0, don't crawl
			print("User %s already exists! Pass!"%user_id)
			"""path1 = str(newpath)+'/followers_list.pickle'
			path2 = str(newpath)+'/friends_list.pickle'
			path3 = str(newpath)+'/list_members.pickle'
			if os.path.exists(path1):
				f1 = open(path1,'rb')
				user_followers_list = pickle.load(f1)
			if os.path.exists(path2):
				f2 = open(path2,'rb')
				user_friends_list = pickle.load(f2)
			if os.path.exists(path3):
				f3 = open(path3,'rb')
				user_list_members = pickle.load(f3)"""
			pass
		else:
			user = api.get_user(user_id)
			try:
				if user.protected != True:	
					lang = (user.lang=='en' or user.lang=='en-GB' or user.lang=='en-gb')
					if user.followers_count<500 and user.friends_count<500 and user.verified==False and lang==True:
					#if user's account is not protected and is not celebrite, record his information
						os.makedirs(newpath)
						profile = getProfile(api,user_id,newpath)
						#--------------------------user's followers---------------------------#
						status = Check_limit(api,0)
						(api, order,fer_total) = Compare_Remain(status,profile['followers_count'],5000,5000,order)
						#print("Order in main: %s" %order)
						user_followers_list = getFollowers(api,user_id,newpath)
						#--------------------------user's friends------------------------------#
						status = Check_limit(api,1)
						(api, order,fing_total) = Compare_Remain(status,profile['friends_count'],5000,5000,order)
						#print("Order in main: %s" %order)
						user_friends_list = getFriends(api,user_id,newpath)
						#--------------------------user's statuses------------------------------#
						status = Check_limit(api,2)
						(api,order,statuses_total) = Compare_Remain(status,profile['statuses_count'],20,3600,order)
						#print("Order in main: %s" %order)
						getStatuses(api,user_id,newpath,statuses_total)
						#--------------------------user's likes----------------------------------#
						status = Check_limit(api,3)
						(api,order,favorites_total) = Compare_Remain(status,profile['favourites_count'],20,300,order)
						#print("Order in main: %s" %order)
						(api,order) = getLikes(api,user_id,newpath,order)
						#------------------------user's lists------------------------------------#
						print("Begin to record list")
						(api,order,user_list_members) = getList(api,user_id,newpath,order)			
					else:
						print("User %s is famous person. Or language is not english %s" %(user_id,user.lang))				
				else:
					print("User %s protected his twitter!" %user_id)
			except tweepy.error.TweepError as e:	#if the account is suspended by twitter
				print(e)
				if e == "User has been suspended":
					pass
	except tweepy.error.RateLimitError as e:
		print ("In crawl_single() Rate limit exceed. This is strange! Try to sleep for 15 minutes!")
		time.sleep(60*15)
	except tweepy.error.TweepError as e:
		print(e)
		print (user_id)
		pass
	return user_followers_list, user_friends_list, user_list_members, api, order

#===================crawl many user at one time==============================#
def crawl_more(user_list,newpath,api,order):		#crawl all the user in the list
	it = 0
	remove_list = []
	while(it<len(user_list)):
		user_followers_list = []
		user_friends_list = []
		user_id = user_list[it]
		(user_followers_list,user_friends_list,user_list_members,api,order)=crawl_single(user_id,newpath,api,order)
		if user_followers_list == []:
			print ("Remove unrecord user %s"%user_list[it])
			remove_list.append(user_list[it])
		it = it + 1
	for d in remove_list:
		user_list.remove(d)
	print(user_list)
	return api,order,user_list

#=====================select seed user and crawl seed user's information=======================#
def recycle_crawl(user_list,path,api,order):		#just crawl seed user's information
	real_p_seed = []
	p_rem = []
	p_followers_list = []
	p_friends_list = []
	p_list_members = []
	for p_seed in user_list:
		try:
			f = open(str(path)+'%s/profile.pickle'%p_seed,'rb')
			p_profile = pickle.load(f)			
			if p_profile['statuses_count']!=0 and ((time_now-p_profile['created_at']).days/p_profile['statuses_count'])<2:	
				activity = ((time_now-p_profile['created_at']).days/p_profile['statuses_count'])		
				print("The activity of user is: %s"%activity)		#select active_user as seed user
				print("Begin to record potential seed user's information %s!"%p_seed)
				real_p_seed.append(p_seed)
				f = open(str(path)+'%s/followers_list.pickle'%p_seed,'rb')
				p_followers_list = pickle.load(f)
				f = open(str(path)+'%s/friends_list.pickle'%p_seed,'rb')
				p_friends_list = pickle.load(f)
				if os.path.exists(str(path)+'%s/list_members.pickle'%p_seed):
					f = open(str(path)+'%s/list_members.pickle'%p_seed,'rb')
					p_list_members = pickle.load(f)
				(ff, fer, fing)=F_and_F(p_followers_list,p_friends_list,p_list_members)
				(api,order,p_remff) = crawl_more(list(ff),path,api,order)
				p_rem.extend(p_remff)
				pickle.dump(p_remff,open(str(path)+'%s/remff.pickle'%p_seed,'wb'))
				(api,order,p_remfer) = crawl_more(list(fer),path,api,order)
				p_rem.extend(p_remfer)
				pickle.dump(p_remfer,open(str(path)+'%s/remfer.pickle'%p_seed,'wb'))
				(api,order,p_remfing) = crawl_more(list(fing),path,api,order)
				p_rem.extend(p_remfing)
				pickle.dump(p_remfing,open(str(path)+'%s/remfing.pickle'%p_seed,'wb'))
				print("Finish record potential seed user %s information"%p_seed)
			else:
				print ("User %s is not active, won't crawl it"%p_seed)
				continue
		except IOError as e:
			print(e)
			print("This shouldn't happen, why no user %s folder?"%p_seed)
			continue
	print("Finish all potential seed user!")
	return api,order,real_p_seed,p_rem

#========================crawl next layer all user===============================#
def crawl_layer(ff_list,fer_list,fing_list,layer,api,order):
	seed_path = create_path("seed/seed_%s/"%layer)
	newpath = create_path("Data", "")
	(api,order,ff_seed,ff_next_remain) = recycle_crawl(ff_list,newpath,api,order)		# 2 represents layer seed blongs
	pickle.dump(ff_seed,open(str(seed_path)+'ff_%s_seed.pickle'%layer,'wb'))	#layer(remain)-layer(seed)=1, seed is selected based on remain
	print ("Create one seed file!")
	(api,order,fer_seed,fer_next_remain) = recycle_crawl(fer_list,newpath,api,order)		# 2 represents layer seed blongs
	pickle.dump(fer_seed,open(str(seed_path)+'fer_%s_seed.pickle'%layer,'wb'))
	(api,order,fing_seed,fing_next_remain) = recycle_crawl(fing_list,newpath,api,order)	
	pickle.dump(fing_seed,open(str(seed_path)+'fing_%s_seed.pickle'%layer,'wb'))
	return ff_next_remain,fer_next_remain,fing_next_remain,api,order

#======================Main() Function===========================================#
def main():
	order = 15
	api = Authentication(order)	
	seed_friends_list = []
	seed_followers_list = []
	#----------------------get seed_user_information-----------------------------#
	newpath = create_path("Data", "")
	(seed_followers_list,seed_friends_list,seed_list_members,api,order)=crawl_single(first_seed_user,newpath,api,order)
	(ff_1, fer_1, fing_1)=F_and_F(seed_followers_list,seed_friends_list,seed_list_members)
	#----------------------get seed user's follower and following information-----------#
	(api,order,ff_1_remain) = crawl_more(list(ff_1),newpath,api,order)
	pickle.dump(ff_1_remain,open(str(newpath)+'%s/remff.pickle'%first_seed_user,'wb'))
	(api,order,fer_1_remain) = crawl_more(list(fer_1),newpath,api,order)
	pickle.dump(fer_1_remain,open(str(newpath)+'%s/remfer.pickle'%first_seed_user,'wb'))
	(api,order,fing_1_remain) = crawl_more(list(fing_1),newpath,api,order)
	pickle.dump(fing_1_remain,open(str(newpath)+'%s/remfing.pickle'%first_seed_user,'wb'))
	print("First seed user %s all information done!" %first_seed_user)

	#-------------------select second_layer_seed user to crawl----------------------------#
	(ff_2_remain,fer_2_remain,fing_2_remain,api,order)=crawl_layer(ff_1_remain,fer_1_remain,fing_1_remain,"2",api,order)
	seed_3 = ff_2_remain + fer_2_remain + fing_2_remain
	os.makedirs(r'seed/seed_3')
	pickle.dump(seed_3,open('seed/seed_3/seed_3_list.pickle','wb'))
	print("Second_layer_seed users' information done!")
	(ff_3_remain,fer_3_remain,fing_3_remain,api,order)=crawl_layer(ff_2_remain,fer_2_remain,fing_2_remain,"3",api,order)
	print("All finished")
#===============================Real Main()=====================================#
if __name__ == '__main__':
	try:
		main()
	except (Timeout, ssl.SSLError, ReadTimeoutError, ConnectionError) as exc:
		print(exc)
		print("Error in main(), try to sleep 5 mins")
		time.sleep(60*5)
