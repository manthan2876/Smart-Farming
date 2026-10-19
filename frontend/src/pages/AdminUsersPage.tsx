import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { getAdminUsers, updateAdminUser } from "../api/admin";
import { AdminUser } from "../api/types";
import { Card, Button, Input, Modal, Badge, Select } from "../components/ui";
import { 
  Users, 
  ShieldCheck, 
  GraduationCap, 
  Sprout, 
  Search, 
  Filter, 
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  UserCheck,
  Phone,
  User as UserIcon
} from "../components/icons";
import { normalizePhoneNumber, isValidPhoneNumber } from "../lib/phone";

export default function AdminUsersPage() {
  const { user: currentUser, token, t } = useAuth();
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("all");
  const [page, setPage] = useState(0);
  const pageSize = 20;

  // Selected user for edit modal
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [userName, setUserName] = useState("");
  const [userPhone, setUserPhone] = useState("");
  const [newRole, setNewRole] = useState<"farmer" | "expert" | "admin">("farmer");
  const [reason, setReason] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["admin_users", page, roleFilter, search],
    queryFn: () =>
      getAdminUsers(token!, {
        skip: page * pageSize,
        limit: pageSize,
        role: roleFilter === "all" ? undefined : roleFilter,
        search: search.trim() || undefined,
      }),
    enabled: !!token,
  });

  const mutation = useMutation({
    mutationFn: async ({
      userId,
      name,
      phone,
      role,
      changeReason,
    }: {
      userId: string;
      name?: string;
      phone?: string;
      role?: "farmer" | "expert" | "admin";
      changeReason?: string;
    }) => {
      return updateAdminUser(token!, userId, {
        name,
        phone,
        role,
        reason: changeReason,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin_users"] });
      setActionSuccess(t("userUpdatedSuccess"));
      setActionError(null);
      setTimeout(() => {
        setSelectedUser(null);
        setActionSuccess(null);
        setReason("");
      }, 1200);
    },
    onError: (err: any) => {
      setActionError(err?.message || "Failed to update user profile.");
    },
  });

  const handleOpenUserModal = (user: AdminUser) => {
    setSelectedUser(user);
    setUserName(user.name || "");
    setUserPhone(user.phone || "");
    setNewRole(user.role);
    setReason("");
    setActionError(null);
    setActionSuccess(null);
  };

  const handleSaveUser = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUser) return;
    if (selectedUser.id === currentUser?.id && newRole !== "admin") {
      setActionError("Security Guard: Administrators cannot demote their own account.");
      return;
    }

    const trimmedPhone = userPhone.trim();
    let normalizedPhone: string | undefined = undefined;
    if (trimmedPhone) {
      if (!isValidPhoneNumber(trimmedPhone)) {
        setActionError(t("phoneInvalid"));
        return;
      }
      normalizedPhone = normalizePhoneNumber(trimmedPhone);
    }

    setActionError(null);
    mutation.mutate({
      userId: selectedUser.id,
      name: userName.trim() || undefined,
      phone: normalizedPhone !== undefined ? normalizedPhone : (trimmedPhone ? trimmedPhone : ""),
      role: newRole,
      changeReason: reason.trim() || undefined,
    });
  };

  const users = data?.users || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / pageSize);

  const isSelf = selectedUser?.id === currentUser?.id;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl text-ink sm:text-4xl">{t("platformUserRoles")}</h1>
          <p className="mt-2 text-sm text-muted">
            {t("userRolesSubtitle")}
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => refetch()}
          disabled={isFetching}
          className="flex items-center gap-2"
        >
          <RefreshCw size={15} className={isFetching ? "animate-spin" : ""} />
          <span>{t("refresh")}</span>
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("totalRegistered")}</h3>
            <Users size={18} className="text-muted" />
          </div>
          <div className="mt-3 font-display text-3xl text-ink">{total}</div>
          <p className="mt-1 text-xs text-muted">{t("matchingFilters")}</p>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("farmers")}</h3>
            <Sprout size={18} className="text-farmer-600" />
          </div>
          <div className="mt-3 font-display text-3xl text-farmer-700 dark:text-farmer-300">
            {users.filter((u) => u.role === "farmer").length}
          </div>
          <p className="mt-1 text-xs text-muted">{t("activeOnPage")}</p>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("fieldExperts")}</h3>
            <GraduationCap size={18} className="text-purple-600 dark:text-purple-400" />
          </div>
          <div className="mt-3 font-display text-3xl text-purple-700 dark:text-purple-400">
            {users.filter((u) => u.role === "expert").length}
          </div>
          <p className="mt-1 text-xs text-muted">{t("activeOnPage")}</p>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("administrators")}</h3>
            <ShieldCheck size={18} className="text-admin-600 dark:text-amber-400" />
          </div>
          <div className="mt-3 font-display text-3xl text-admin-700 dark:text-amber-400">
            {users.filter((u) => u.role === "admin").length}
          </div>
          <p className="mt-1 text-xs text-muted">{t("protectedTier")}</p>
        </Card>
      </div>

      {/* Filters */}
      <Card className="flex flex-col gap-4 sm:flex-row sm:items-center justify-between" padding="md">
        <div className="flex flex-1 flex-col gap-3 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
            <Input
              placeholder={t("searchUsersPlaceholder")}
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(0);
              }}
              className="pl-9"
            />
          </div>
          <div className="flex items-center gap-2">
            <Select
              value={roleFilter}
              onChange={(val) => {
                setRoleFilter(val);
                setPage(0);
              }}
              theme="admin"
              leadingIcon={<Filter size={15} className="text-admin-700 dark:text-amber-400" />}
              options={[
                { value: "all", label: t("allRoles") },
                { value: "farmer", label: t("farmers"), icon: <Sprout size={14} className="text-farmer-600 dark:text-farmer-400 shrink-0" /> },
                { value: "expert", label: t("fieldExperts"), icon: <GraduationCap size={14} className="text-expert-700 dark:text-cyan-400 shrink-0" /> },
                { value: "admin", label: t("administrators"), icon: <ShieldCheck size={14} className="text-admin-700 dark:text-amber-400 shrink-0" /> },
              ]}
              className="min-w-[160px]"
            />
          </div>
        </div>
      </Card>

      {/* Users Table */}
      <Card padding="none" className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-line bg-canvas text-xs uppercase text-muted">
              <tr>
                <th className="px-6 py-4 font-semibold">{t("user")}</th>
                <th className="px-6 py-4 font-semibold">{t("phoneOrEmail")}</th>
                <th className="px-6 py-4 font-semibold">{t("role")}</th>
                <th className="px-6 py-4 font-semibold">{t("farm")} & {t("location")}</th>
                <th className="px-6 py-4 font-semibold text-center">{t("scan")}</th>
                <th className="px-6 py-4 font-semibold">{t("registered")}</th>
                <th className="px-6 py-4 font-semibold text-right">{t("actions")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-muted">
                    {t("loadingUsers")}
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-muted">
                    {t("noUsersFound")}
                  </td>
                </tr>
              ) : (
                users.map((u) => {
                  const roleBadgeVariant =
                    u.role === "admin"
                      ? "blue"
                      : u.role === "expert"
                      ? "purple"
                      : "green";

                  return (
                    <tr key={u.id} className="hover:bg-canvas/50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-farmer-100 font-bold text-farmer-800 dark:bg-farmer-900/80 dark:text-farmer-200 dark:border dark:border-farmer-700">
                            {u.name ? u.name.charAt(0).toUpperCase() : "U"}
                          </div>
                          <div>
                            <div className="font-semibold text-ink flex items-center gap-2">
                              {u.name || t("unnamedUser")}
                              {u.id === currentUser?.id && (
                                <span className="rounded bg-farmer-100 px-1.5 py-0.2 text-[0.65rem] font-bold text-farmer-800 dark:bg-farmer-900/80 dark:text-farmer-200 dark:border dark:border-farmer-700">
                                  {t("you")}
                                </span>
                              )}
                            </div>
                            <div className="text-xs text-muted font-mono">{u.id.slice(0, 8)}...</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-ink">{u.email || "N/A"}</div>
                        <div className="text-xs text-muted">{u.phone || "N/A"}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className="inline-flex whitespace-nowrap items-center gap-1.5 rounded-xs border border-line bg-canvas px-2 py-0.5 text-xs font-semibold text-ink"
                        >
                          {u.role === "admin" && <ShieldCheck size={13} />}
                          {u.role === "expert" && <GraduationCap size={13} />}
                          {u.role === "farmer" && <Sprout size={13} />}
                          <span className="capitalize whitespace-nowrap">{u.role === "admin" ? t("roleAdmin") : u.role === "expert" ? t("roleExpert") : t("roleFarmer")}</span>
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-ink font-medium">{u.farm_name || t("noFarmRegistered")}</div>
                        <div className="text-xs text-muted">{u.farm_location || "N/A"}</div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className="font-semibold text-ink">{u.scan_count}</span>
                      </td>
                      <td className="px-6 py-4 text-xs text-muted">
                        {u.created_at ? new Date(u.created_at).toLocaleDateString() : "N/A"}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleOpenUserModal(u)}
                          className="text-xs font-semibold whitespace-nowrap min-w-max"
                        >
                          {t("editUser")}
                        </Button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between border-t border-line px-6 py-3 bg-canvas/40">
            <span className="text-xs text-muted">
              {t("showingPage")} {page + 1} {t("of")} {totalPages} ({total} {t("users")})
            </span>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
              >
                {t("previous")}
              </Button>
              <Button
                variant="secondary"
                size="sm"
                disabled={page >= totalPages - 1}
                onClick={() => setPage((p) => p + 1)}
              >
                {t("next")}
              </Button>
            </div>
          </div>
        )}
      </Card>

      {/* Edit User & Role Modal */}
      <Modal
        open={!!selectedUser}
        title={t("manageUser")}
        onClose={() => {
          if (!mutation.isPending) setSelectedUser(null);
        }}
      >
        {selectedUser && (
          <form onSubmit={handleSaveUser} className="space-y-4">
            <div className="rounded-md bg-canvas p-4 text-sm">
              <div className="flex items-center justify-between">
                <div className="font-semibold text-ink">{selectedUser.name || t("unnamedUser")}</div>
                <span className="rounded bg-surface px-2 py-0.5 text-xs font-bold capitalize text-ink border border-line">
                  {selectedUser.role}
                </span>
              </div>
              <div className="mt-1 text-xs text-muted">{selectedUser.email || t("noEmailLinked")}</div>
            </div>

            {isSelf && (
              <div className="flex items-start gap-2 rounded-md bg-amber-50 p-3 text-xs text-amber-800 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800/80">
                <AlertCircle size={16} className="shrink-0 mt-0.5" />
                <span>
                  <strong>{t("selfDemotionGuard")}:</strong> {t("selfDemotionDesc")}
                </span>
              </div>
            )}

            <div>
              <label className="mb-1 block text-xs font-semibold text-ink">{t("fullName")}</label>
              <Input
                placeholder={t("enterFullName")}
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                leadingIcon={<UserIcon size={15} />}
              />
            </div>

            <div>
              <label className="mb-1 block text-xs font-semibold text-ink">{t("mobilePhone")}</label>
              <Input
                placeholder="e.g. 9999999999 or +919999999999"
                value={userPhone}
                onChange={(e) => setUserPhone(e.target.value)}
                leadingIcon={<Phone size={15} />}
              />
              <span className="mt-1 block text-xs text-muted">
                {t("phoneHelp")}
              </span>
            </div>

            <div>
              <label className="mb-1 block text-xs font-semibold text-ink">{t("selectNewRole")}</label>
              <Select
                value={newRole}
                onChange={(val) => setNewRole(val as "farmer" | "expert" | "admin")}
                disabled={isSelf && newRole === "admin"}
                theme="admin"
                options={[
                  { value: "farmer", label: `Farmer / Grower (${t("farmerFieldAccuracy")})`, icon: <Sprout size={14} className="text-farmer-600 dark:text-farmer-400 shrink-0" /> },
                  { value: "expert", label: `Field Expert / Specialist (${t("expertTriageQueue")})`, icon: <GraduationCap size={14} className="text-expert-700 dark:text-cyan-400 shrink-0" /> },
                  { value: "admin", label: `Administrator (${t("administrators")})`, icon: <ShieldCheck size={14} className="text-admin-700 dark:text-amber-400 shrink-0" /> },
                ]}
              />
            </div>

            <div>
              <label className="mb-1 block text-xs font-semibold text-ink">
                {t("auditReason")} <span className="text-muted font-normal">({t("optional")})</span>
              </label>
              <Input
                placeholder={t("auditReasonPlaceholder")}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </div>

            {actionError && (
              <div className="flex items-center gap-2 rounded-md bg-red-50 p-3 text-xs text-red-700 border border-red-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800/80">
                <AlertCircle size={15} className="shrink-0" />
                <span>{actionError}</span>
              </div>
            )}

            {actionSuccess && (
              <div className="flex items-center gap-2 rounded-md bg-emerald-50 p-3 text-xs text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/80">
                <CheckCircle2 size={15} className="shrink-0" />
                <span>{actionSuccess}</span>
              </div>
            )}

            <div className="flex justify-end gap-3 pt-3">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setSelectedUser(null)}
                disabled={mutation.isPending}
              >
                {t("cancel")}
              </Button>
              <Button
                type="submit"
                disabled={mutation.isPending || (isSelf && newRole !== "admin")}
                className="flex items-center gap-2"
              >
                <UserCheck size={16} />
                <span>{mutation.isPending ? t("updating") : t("save")}</span>
              </Button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
}
