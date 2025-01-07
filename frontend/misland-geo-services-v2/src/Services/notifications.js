import { Notify } from "quasar";
export async function negative({ message, time, position, closeBtn, color, multiLine }) {
  await Notify.create({
    icon: !closeBtn ? '' : '',
    position: position || "top-right",
    message: `${message}`,
    closeBtn: closeBtn || false,
    timeout: typeof time === 'number' ? time : 3500,
    badgeStyle: "opacity: 0",
    color: color || 'red',
    multiLine: multiLine ? multiLine : false,
    html: true,
  });

}
export async function positive({ message, time, position, closeBtn, color, multiLine }) {
  await Notify.create({
    icon: !closeBtn ? '' : '',
    position: position || "top-right",
    message: `${message}`,
    closeBtn: closeBtn || false,
    timeout: typeof time === 'number' ? time : 3500,
    badgeStyle: "opacity: 0",
    color: color || 'secondary',
    multiLine: multiLine ? multiLine : false,
    html: true,
  });


}
