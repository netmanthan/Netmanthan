# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from datetime import datetime
from functools import wraps
from typing import Callable

from werkzeug.wrappers import Response

import netmanthan
from netmanthan import _
from netmanthan.utils import cint


def apply():
	rate_limit = netmanthan.conf.rate_limit
	if rate_limit:
		netmanthan.local.rate_limiter = RateLimiter(rate_limit["limit"], rate_limit["window"])
		netmanthan.local.rate_limiter.apply()


def update():
	if hasattr(netmanthan.local, "rate_limiter"):
		netmanthan.local.rate_limiter.update()


def respond():
	if hasattr(netmanthan.local, "rate_limiter"):
		return netmanthan.local.rate_limiter.respond()


class RateLimiter:
	def __init__(self, limit, window):
		self.limit = int(limit * 1000000)
		self.window = window

		self.start = datetime.utcnow()
		timestamp = int(netmanthan.utils.now_datetime().timestamp())

		self.window_number, self.spent = divmod(timestamp, self.window)
		self.key = netmanthan.cache().make_key(f"rate-limit-counter-{self.window_number}")
		self.counter = cint(netmanthan.cache().get(self.key))
		self.remaining = max(self.limit - self.counter, 0)
		self.reset = self.window - self.spent

		self.end = None
		self.duration = None
		self.rejected = False

	def apply(self):
		if self.counter > self.limit:
			self.rejected = True
			self.reject()

	def reject(self):
		raise netmanthan.TooManyRequestsError

	def update(self):
		self.end = datetime.utcnow()
		self.duration = int((self.end - self.start).total_seconds() * 1000000)

		pipeline = netmanthan.cache().pipeline()
		pipeline.incrby(self.key, self.duration)
		pipeline.expire(self.key, self.window)
		pipeline.execute()

	def headers(self):
		headers = {
			"X-RateLimit-Reset": self.reset,
			"X-RateLimit-Limit": self.limit,
			"X-RateLimit-Remaining": self.remaining,
		}
		if self.rejected:
			headers["Retry-After"] = self.reset
		else:
			headers["X-RateLimit-Used"] = self.duration

		return headers

	def respond(self):
		if self.rejected:
			return Response(_("Too Many Requests"), status=429)


def rate_limit(
	key: str = None,
	limit: int | Callable = 5,
	seconds: int = 24 * 60 * 60,
	methods: str | list = "ALL",
	ip_based: bool = True,
):
	"""Decorator to rate limit an endpoint.

	This will limit Number of requests per endpoint to `limit` within `seconds`.
	Uses redis cache to track request counts.

	:param key: Key is used to identify the requests uniqueness (Optional)
	:param limit: Maximum number of requests to allow with in window time
	:type limit: Callable or Integer
	:param seconds: window time to allow requests
	:param methods: Limit the validation for these methods.
	        `ALL` is a wildcard that applies rate limit on all methods.
	:type methods: string or list or tuple
	:param ip_based: flag to allow ip based rate-limiting
	:type ip_based: Boolean

	:returns: a decorator function that limit the number of requests per endpoint
	"""

	def ratelimit_decorator(fun):
		@wraps(fun)
		def wrapper(*args, **kwargs):
			# Do not apply rate limits if method is not opted to check
			if (
				methods != "ALL"
				and netmanthan.request
				and netmanthan.request.method
				and netmanthan.request.method.upper() not in methods
			):
				return netmanthan.call(fun, **netmanthan.form_dict or kwargs)

			_limit = limit() if callable(limit) else limit

			ip = netmanthan.local.request_ip if ip_based is True else None

			user_key = netmanthan.form_dict[key] if key else None

			identity = None

			if key and ip_based:
				identity = ":".join([ip, user_key])

			identity = identity or ip or user_key

			if not identity:
				netmanthan.throw(_("Either key or IP flag is required."))

			cache_key = f"rl:{netmanthan.form_dict.cmd}:{identity}"

			value = netmanthan.cache().get(cache_key) or 0
			if not value:
				netmanthan.cache().setex(cache_key, seconds, 0)

			value = netmanthan.cache().incrby(cache_key, 1)
			if value > _limit:
				netmanthan.throw(
					_("You hit the rate limit because of too many requests. Please try after sometime.")
				)

			return netmanthan.call(fun, **netmanthan.form_dict or kwargs)

		return wrapper

	return ratelimit_decorator
