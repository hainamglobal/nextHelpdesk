<template>
	<div>
		<Dialog
			:options="{ title: 'Thêm nhân viên' }"
			:show="show"
			@close="close()"
		>
			<template #body-content>
				<div class="space-y-3">
					<form 
						class="flex flex-row space-x-2 items-start relative w-full"
						@submit.prevent="() => { if(currentInputIsValidEmail) { addToInviteQueue(searchInput); clearSearchInput(); } }"
					>
						<div class="w-full">
							<Popover class="w-full">
							<template #target="{ open: openPopover, close: closePopover }">
								<div id="inputWrapperDiv" ref="inputWrapperRef" class="w-full">
									<Input
										id="searchInput"
										class="w-full"
										type="text"
										v-model="searchInput"
										placeholder="Nhập email..."
										@input="(val) => { onSearchInputChange(val); openPopover(); }"
										@focus="() => { updateDropdownWidth(); onInputFocus(); openPopover(); }"
										@click="() => { updateDropdownWidth(); onInputFocus(); openPopover(); }"
										@blur="() => { onInputBlur(); closePopover(); }"
									/>
								</div>
							</template>
							<template #body="{ close: closePopover }">
								<div 
									v-show="emailOptions.length > 0"
									class="bg-white border rounded shadow-lg z-[9999] max-h-48 overflow-y-auto overflow-x-hidden mt-1"
									:style="{ width: dropdownWidth, minWidth: dropdownWidth, maxWidth: dropdownWidth }"
								>
									<div 
										v-for="opt in emailOptions" 
										:key="opt.value"
										class="px-3 py-2 cursor-pointer hover:bg-gray-100 flex items-center"
										@mousedown.prevent="() => { selectEmail(opt.value); closePopover() }"
									>
										<Avatar v-if="opt.user_image" :image="opt.user_image" size="sm" class="mr-2" />
										<Avatar v-else :label="opt.label" size="sm" class="mr-2" />
										<div class="flex flex-col text-sm leading-tight overflow-hidden">
											<span class="font-medium truncate">{{ opt.full_name || opt.value }}</span>
											<span class="text-gray-500 text-xs truncate" v-if="opt.full_name">{{ opt.value }}</span>
										</div>
									</div>
								</div>
							</template>
						</Popover>
						</div>
						<Button
							appearance="primary"
							type="submit"
							class="shrink-0"
							:disabled="!currentInputIsValidEmail"
							@click="
								() => {
									addToInviteQueue(searchInput)
									clearSearchInput()
								}
							"
						>
							Thêm
						</Button>
					</form>
					<div
						class="bg-gray-100 min-h-[100px] max-h-[300px] overflow-y-auto px-2 rounded border flex flex-col"
						v-if="inviteQueue.length"
					>
						<ul
							class="flex flex-wrap gap-2 py-2"
						>
							<li
								class="flex items-center p-1 space-x-2 bg-white shadow rounded"
								v-for="email in inviteQueue.slice().reverse()"
								:key="email"
								:title="email"
							>
								<span class="text-base ml-2">
									{{ email }}
								</span>
								<button
									class="grid w-4 h-4 text-gray-700 rounded hover:bg-gray-300 place-items-center"
									@click="removeEmailFromQueue(email)"
								>
									<FeatherIcon class="w-3" name="x" />
								</button>
							</li>
						</ul>
					</div>
				</div>
			</template>
			<template #actions v-if="inviteQueue.length">
				<Button
					:disabled="inviteQueue.length == 0"
					appearance="primary"
					@click="sentInvites()"
					class="mr-2"
					:loading="$resources.sentInvites.loading"
					>Gửi lời mời</Button
				>
				<Button appearance="secondary" class="mr-2" @click="close()">Hủy</Button>
				<div class="grow">
					<Button
						@click="removeAllEmailFromQueue()"
						v-if="inviteQueue.length > 1"
					>
						Xóa tất cả
					</Button>
				</div>
			</template>
		</Dialog>
	</div>
</template>

<script>
import { Dialog, Input, FeatherIcon, Avatar, Popover } from "frappe-ui"
import { ref, watch } from "vue"
import { showGlobalError } from "@/utils"
import { useAgentStore } from "@/stores/agent"

export default {
	name: "AddNewAgentsDialog",
	props: ["show"],
	components: {
		Dialog,
		Input,
		FeatherIcon,
		Avatar,
		Popover,
	},
	setup(props) {
		const searchInput = ref("")
		const inviteQueue = ref([])
		const emailOptions = ref([])
		const showDropdown = ref(false)
		const inputWrapperRef = ref(null)
		const dropdownWidth = ref("100%")

		const currentInputIsValidEmail = ref(false)

		const updateDropdownWidth = () => {
			const inputEl = document.getElementById("inputWrapperDiv")
			if (inputEl) {
				dropdownWidth.value = inputEl.offsetWidth + "px"
			}
		}

		watch(() => props.show, (newVal) => {
			if (!newVal) {
				showDropdown.value = false;
			}
		});

		return {
			searchInput,
			inviteQueue,
			currentInputIsValidEmail,
			emailOptions,
			showDropdown,
			inputWrapperRef,
			dropdownWidth,
			updateDropdownWidth,
		}
	},
	methods: {
		testEmailRegex(val) {
			let emailRegex = /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/
			return emailRegex.test(val)
		},
		async searchEmailsFromAPI(query) {
			const agentStore = useAgentStore()
			try {
				let res = await agentStore.searchUser(query || "")
				if (res && res.data) {
					this.emailOptions = res.data.map(u => ({
						label: u.full_name ? `${u.full_name} (${u.email})` : u.email,
						value: u.email,
						full_name: u.full_name,
						user_image: u.user_image
					}))
					if (this.emailOptions.length > 0) {
						this.showDropdown = true
					}
				}
			} catch (err) {
				console.error("Search failed", err)
			}
		},
		onInputFocus() {
			this.searchEmailsFromAPI(this.searchInput)
		},
		onInputBlur() {
			// We use mousedown.prevent on the items to avoid blur triggering before select
			this.showDropdown = false
		},
		selectEmail(email) {
			this.addToInviteQueue(email)
			this.clearSearchInput()
		},
		onSearchInputChange(val) {
			val = val.replaceAll(" ", "")

			if (val == "") {
				document.getElementById("searchInput").value = ""
				this.showDropdown = false
				this.emailOptions = []
				this.searchEmailsFromAPI("") // Fetch defaults again
				return
			}

			const valStr = val
			const inputs = val.split(",")

			let clearInputFlag = false
			this.currentInputIsValidEmail = false
			inputs.forEach((input) => {
				if (this.testEmailRegex(input)) {
					if (inputs.length > 1) {
						this.addToInviteQueue(input)
						clearInputFlag = true
					} else {
						if (valStr.includes(",")) {
							this.addToInviteQueue(input)
							clearInputFlag = true
						} else {
							this.currentInputIsValidEmail = true
						}
					}
				}
			})
			if (clearInputFlag) {
				this.clearSearchInput()
			} else {
				this.searchEmailsFromAPI(val)
			}
		},
		addToInviteQueue(email) {
			this.inviteQueue = [...new Set([...this.inviteQueue, email])]
		},
		removeEmailFromQueue(email) {
			this.inviteQueue = this.inviteQueue.filter((item) => item !== email)
		},
		removeAllEmailFromQueue() {
			this.inviteQueue = []
		},
		clearSearchInput() {
			this.currentInputIsValidEmail = false
			this.searchInput = ""
			this.showDropdown = false

			const input = document.getElementById("searchInput")
			if (input) {
				input.value = ""
				input.focus()
			}
		},
		close() {
			this.searchInput = ""
			this.showDropdown = false
			this.emailOptions = []
			this.inviteQueue = []
			this.$emit("close")
		},
		sentInvites() {
			this.$resources.sentInvites.submit({
				emails: this.inviteQueue,
			})
		},
	},
	resources: {
		sentInvites() {
			return {
				url: "helpdesk.api.agent.sent_invites",
				onSuccess: (res) => {
					this.currentInputIsValidEmail = false
					this.searchInput = ""
					this.inviteQueue = []

					this.$toast({
						title: "Gửi lời mời thành công!",
						icon: "check",
						iconClasses: "text-green-500"
					})

					this.$emit("success", res)
					this.close()
				},
				onError: (err) => {
					if (err.exc_type == "PaywallReachedError") {
						this.$toast({
							title: "Đạt giới hạn nhân viên!",
							text: "Bạn đã đạt số lượng nhân viên tối đa. Vui lòng nâng cấp gói để thêm nhiều nhân viên hơn.",
							icon: "x",
							iconClasses: "text-red-500",
						})
					} else {
						showGlobalError(err);
					}
				},
			}
		},
	},
}
</script>
