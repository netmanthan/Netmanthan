<template>
	<div>
		<div class="row form-section visible-section shaded-section">
			<div class="section-body">
				<div class="form-column col-sm-12">
					<form>
						<div class="netmanthan-control" :data-fieldtype="column.type" v-for="(column, index) in columns" :key="index" :class="column.class">
							<div class="form-group">
								<div class="clearfix"><label class="control-label">{{ column.label }}</label></div>
								<div class="control-value like-disabled-input" v-html="column.formatter ? column.formatter(request[column.slug]) : request[column.slug]"></div>
							</div>
						</div>
					</form>
				</div>
			</div>
		</div>
		<div class="row form-section visible-section">
			<div class="col-sm-10">
				<h6 class="form-section-heading uppercase">{{ __("SQL Queries") }}</h6>
			</div>
			<div class="col-sm-2 filter-list">
				<div class="sort-selector">
					<div class="dropdown"><a class="text-muted dropdown-toggle small" data-toggle="dropdown"><span class="dropdown-text">{{ table_columns.filter(c => c.slug == query.sort)[0].label }}</span></a>
						<ul class="dropdown-menu">
							<li v-for="(column, index) in table_columns.filter(c => c.sortable)" :key="index" @click="query.sort = column.slug"><a class="option">{{ column.label }}</a></li>
						</ul>
					</div>
					<button class="btn btn-default btn-xs btn-order" @click="query.order = (query.order == 'asc') ? 'desc' : 'asc'">
						<span class="octicon text-muted" :class="query.order == 'asc' ? 'octicon-arrow-down' : 'octicon-arrow-up'"></span>
					</button>
				</div>
			</div>
			<div class="section-body">
				<div class="form-column col-sm-12">
					<form>
						<div class="form-group netmanthan-control input-max-width" data-fieldtype="Check">
							<div class="checkbox">
								<label>
									<span class="input-area"><input type="checkbox" class="input-with-feedback bold" data-fieldtype="Check" v-model="group_duplicates"></span>
									<span class="label-area small">{{ __("Group Duplicate Queries") }}</span>
								</label>
							</div>
						</div>
						<div class="netmanthan-control" data-fieldtype="Table">
							<div>
								<div class="form-grid">
									<div class="grid-heading-row">
										<div class="grid-row">
											<div class="data-row row">
												<div class="row-index col col-xs-1">
													<span>{{ __("Index") }}</span></div>
												<div class="col grid-static-col col-xs-6">
													<div class="static-area ellipsis">{{ __("Query") }}</div>
												</div>
												<div class="col grid-static-col col-xs-2">
													<div class="static-area ellipsis text-right">{{ __("Duration (ms)") }}</div>
												</div>
												<div class="col grid-static-col col-xs-1">
													<div class="static-area ellipsis text-right">{{ __("Exact Copies") }}</div>
												</div>
												<div class="col grid-static-col col-xs-1">
													<div class="static-area ellipsis text-right">{{ __("Normalized Copies") }}</div>
												</div>
											</div>
										</div>
									</div>
									<div class="grid-body">
										<div class="rows">
											<div class="grid-row" :class="showing == call.index ? 'grid-row-open' : ''"  v-for="call in paginated(sorted(grouped(request.calls)))" :key="call.index">
												<div class="data-row row" @click="showing = showing == call.index ? null : call.index" >
													<div class="row-index col col-xs-1"><span>{{ call.index }}</span></div>
													<div class="col grid-static-col col-xs-6" data-fieldtype="Code">
														<div class="static-area"><span>{{ call.query }}</span></div>
													</div>
													<div class="col grid-static-col col-xs-2">
														<div class="static-area ellipsis text-right">{{ call.duration }}</div>
													</div>
													<div class="col grid-static-col col-xs-1">
														<div class="static-area ellipsis text-right">{{ call.exact_copies }}</div>
													</div>
													<div class="col grid-static-col col-xs-1">
														<div class="static-area ellipsis text-right">{{ call.normalized_copies }}</div>
													</div>
													<div class="col col-xs-1"><a class="close btn-open-row">
														<span class="octicon" :class="showing == call.index? 'octicon-triangle-up' : 'octicon-triangle-down'"></span></a>
													</div>
												</div>
												<div class="recorder-form-in-grid" v-if="showing == call.index">
													<div class="grid-form-heading" @click="showing = null">
														<div class="toolbar grid-header-toolbar">
															<span class="panel-title">{{ __("SQL Query") }} #<span class="grid-form-row-index">{{ call.index }}</span></span>
														</div>
													</div>
													<div class="grid-form-body">
														<div class="form-area">
															<div class="form-layout">
																<div class="form-page">
																	<div class="row form-section visible-section">
																		<div class="section-body">
																			<div class="form-column col-sm-12">
																				<form>
																					<div class="netmanthan-control">
																						<div class="form-group">
																							<div class="clearfix"><label class="control-label">{{ __("Query") }}</label></div>
																							<div class="control-value like-disabled-input for-description"><pre>{{ call.query }}</pre></div>
																						</div>
																					</div>
																					<div class="netmanthan-control">
																						<div class="form-group">
																							<div class="clearfix"><label class="control-label">{{ __("Normalized Query") }}</label></div>
																							<div class="control-value like-disabled-input for-description"><pre>{{ call.normalized_query }}</pre></div>
																						</div>
																					</div>
																					<div class="netmanthan-control input-max-width">
																						<div class="form-group">
																							<div class="clearfix"><label class="control-label">{{ __("Duration (ms)") }}</label></div>
																							<div class="control-value like-disabled-input">{{ call.duration }}</div>
																						</div>
																					</div>
																					<div class="netmanthan-control input-max-width">
																						<div class="form-group">
																							<div class="clearfix"><label class="control-label">{{ __("Exact Copies") }}</label></div>
																							<div class="control-value like-disabled-input">{{ call.exact_copies }}</div>
																						</div>
																					</div>
																					<div class="netmanthan-control input-max-width">
																						<div class="form-group">
																							<div
																								class="clearfix"><label class="control-label">{{ __("Normalized Copies") }}</label></div>
																							<div class="control-value like-disabled-input">{{ call.normalized_copies }}</div>
																						</div>
																					</div>
																					<div class="netmanthan-control">
																						<div class="form-group">
																							<div class="clearfix"><label class="control-label">{{ __("Stack Trace") }}</label></div>
																							<div class="control-value like-disabled-input for-description" style="overflow:auto">
																								<table class="table table-striped">
																									<thead>
																										<tr>
																											<th v-for="key in ['filename', 'lineno', 'function']" :key="key">{{ key }}</th>
																										</tr>
																									</thead>
																									<tbody>
																										<template v-for="(row, index) in call.stack">
																											<tr :key="index">
																												<td v-for="key in ['filename', 'lineno', 'function']" :key="key">{{ row[key] }}</td>
																											</tr>
																										</template>
																									</tbody>
																								</table>
																							</div>
																						</div>
																					</div>
																					<div class="netmanthan-control" v-if="call.explain_result[0]">
																						<div class="form-group">
																							<div class="clearfix"><label class="control-label">{{ __("SQL Explain") }}</label></div>
																							<div class="control-value like-disabled-input for-description" style="overflow:auto">
																								<table class="table table-striped">
																									<thead>
																										<tr>
																											<th v-for="key in Object.keys(call.explain_result[0])" :key="key">{{ key }}</th>
																										</tr>
																									</thead>
																									<tbody>
																										<tr v-for="(row, index) in call.explain_result" :key="index">
																											<td v-for="key in Object.keys(call.explain_result[0])" :key="key">{{ row[key] }}</td>
																										</tr>
																									</tbody>
																								</table>
																							</div>
																						</div>
																					</div>
																				</form>
																			</div>
																		</div>
																	</div>
																</div>
															</div>
														</div>
													</div>
												</div>
											</div>
										</div>
										<div v-if="request.calls.length == 0" class="grid-empty text-center">{{ __("No Data") }}</div>
									</div>
								</div>
							</div>
						</div>
					</form>
				</div>
			</div>
			<div v-if="request.calls.length != 0" class="list-paging-area" style="border-top: none">
				<div class="row">
					<div class="col-xs-6">
						<div class="btn-group btn-group-paging">
							<button type="button" class="btn btn-default btn-sm" v-for="(limit, index) in [20, 50, 100]" :key="index" :class="query.pagination.limit == limit ? 'btn-info' : ''" @click="query.pagination.limit = limit">
								{{ limit }}
							</button>
						</div>
					</div>
					<div class="col-xs-6 text-right">
						<div class="btn-group btn-group-paging">
							<button type="button" class="btn btn-default btn-sm" :class="page.status" v-for="(page, index) in pages" :key="index" @click="query.pagination.page = page.number">
								{{ page.label }}
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: "RequestDetail",
 	data() {
		return {
			columns: [
				{label: __("Path"), slug: "path", type: "Data", class: "col-sm-6"},
				{label: __("CMD"), slug: "cmd", type: "Data", class: "col-sm-6"},
				{label: __("Time"), slug: "time", type: "Time", class: "col-sm-6"},
				{label: __("Duration (ms)"), slug: "duration", type: "Float", class: "col-sm-6"},
				{label: __("Number of Queries"), slug: "queries", type: "Int", class: "col-sm-6"},
				{label: __("Time in Queries (ms)"), slug: "time_queries", type: "Float", class: "col-sm-6"},
				{label: __("Request Headers"), slug: "headers", type: "Small Text", formatter: value => `<pre class="for-description like-disabled-input">${JSON.stringify(value, null, 4)}</pre>`, class: "col-sm-12"},
				{label: __("Form Dict"), slug: "form_dict", type: "Small Text", formatter: value => `<pre class="for-description like-disabled-input">${JSON.stringify(value, null, 4)}</pre>`, class: "col-sm-12"},
			],
			table_columns: [
				{label: __("Execution Order"), slug: "index", sortable: true},
				{label: __("Duration (ms)"), slug: "duration", sortable: true},
				{label: __("Exact Copies"), slug: "exact_copies", sortable: true},
			],
			query: {
				sort: "duration",
				order: "desc",
				pagination: {
					limit: 20,
					page: 1,
					total: 0,
				}
			},
			group_duplicates: false,
			showing: null,
			request: {
				calls: [],
			},
		};
	},
	computed: {
		pages: function() {
			const current_page = this.query.pagination.page;
			const total_pages = this.query.pagination.total;
			return [{
				label: __("First"),
				number: 1,
				status: (current_page == 1) ? "disabled" : "",
			},{
				label: __("Previous"),
				number: Math.max(current_page - 1, 1),
				status: (current_page == 1) ? "disabled" : "",
			}, {
				label: current_page,
				number: current_page,
				status: "btn-info",
			}, {
				label: __("Next"),
				number: Math.min(current_page + 1, total_pages),
				status: (current_page == total_pages) ? "disabled" : "",
			}, {
				label: __("Last"),
				number: total_pages,
				status: (current_page == total_pages) ? "disabled" : "",
			}];
		}
	},
	methods: {
		paginated: function(calls) {
			calls = calls.slice();
			this.query.pagination.total = Math.ceil(calls.length / this.query.pagination.limit);
			const begin = (this.query.pagination.page - 1) * (this.query.pagination.limit);
			const end = begin + this.query.pagination.limit;
			return calls.slice(begin, end);
		},
		sorted: function(calls) {
			calls = calls.slice();
			const order = (this.query.order == "asc") ? 1 : -1;
			const sort = this.query.sort;
			return calls.sort((a,b) => (a[sort] > b[sort]) ? order : -order);
		},
		grouped: function(calls) {
			if(this.group_duplicates) {
				calls = calls.slice();
				return calls.uniqBy(call => call["query"]);
			}
			return calls
		},
	},
	mounted() {
		netmanthan.breadcrumbs.add({
			type: 'Custom',
			label: __('Recorder'),
			route: '/app/recorder'
		});

		const request = this.$route.params.request;
		if (request.headers || request.form_dict || request.calls) {
			// complete request data passed as parameter.
			this.request = request;
		} else {
			netmanthan.call({
				method: "netmanthan.recorder.get",
				args: {
					uuid: request.uuid
				}
			}).then( r => {
				this.request = r.message
			});
		}
	},
};
</script>
